import scrapy


#run scrapy shell to test scrapy extract which content
#scrapy shell "https://ncode.syosetu.com/n3436hb/2/"
#scrapy shell "https://ncode.syosetu.com/n9669bk/13/"
#Need to move inside the project directory where scrapy.cfg file exists to run the spider
# cd SyosetsuScraper/src/scraper , cd scraper
# scrapy crawl syosetsu -o test2.json
# scrapy crawl syosetsu -o testjl.jl

class SyosetsuSpider(scrapy.Spider):
    name = "syosetsu"
    start_urls = [
        #'https://ncode.syosetu.com/n3436hb/1/',
        'https://ncode.syosetu.com/n8802bq/1/',
    ]

    def parse(self, response):
        yield {
            'novel_title': response.xpath('//div[@class="contents1"]/a[@class="margin_r20"]/text()').get(),
            'volum_title': response.xpath('//p[@class="chapter_title"]/text()').get(),
            'chapter_number': response.xpath('//div[@id="novel_no"]/text()').get().split("/")[0],
            'chapter_title': response.xpath('//p[@class="novel_subtitle"]/text()').get(),
            'chapter_preword': response.xpath('//div[@id="novel_color"]/div[@id="novel_p"]/p/text()').getall(),
            'chapter_text': "".join(response.xpath('//div[@id="novel_color"]/div[@id="novel_honbun"]/p/text()').getall()),
            'chapter_afterword': response.xpath('//div[@id="novel_color"]/div[@id="novel_a"]/p/text()').getall()
        }

        next_page = response.xpath('//div[@class="novel_bn"]/a/@href')[1].get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)



    def parse2(self, response):
        #character introduction - 登場人物紹介

        #get next page hreft
        # response.xpath('//div[@class="novel_bn"]/a/@href')[1].get()
        # response.css('div.novel_bn a::attr(href)')[1].get()

        #head data
        response.xpath('//head/title/text()').get()
        response.xpath('//head/meta[@property="og:title"]/@content').get()

        #get attributes content
        response.xpath('//head/meta[@property="og:description"]/@content').get()
        response.xpath('//head/meta/@title')


        #main text content
        response.xpath('//*[(@id = "novel_honbun")]').get()
        response.xpath('//p[@class="chapter_title"]/text()').get()

        #xpath to the novel main text content #response.xpath('//body/div[@id="container"]/div[@id="novel_contents"]/div[@id="novel_color"]/div[@id="novel_honbun"]/p')
        title = response.xpath('//div[@class="contents1"]/a[@class="margin_r20"]/text()').get()
        volume_title_text = response.xpath('//p[@class="chapter_title"]/text()').get()
        novel_chapter_numbers = response.xpath('//div[@id="novel_no"]/text()').get()
        first_chapter_number, last_chapter_number = response.xpath('//div[@id="novel_no"]/text()').get().split("/")

        chapter_title = response.xpath('//p[@class="novel_subtitle"]/text()').get()
        chapter_text = response.xpath('//div[@id="novel_color"]/div[@id="novel_honbun"]/p/text()').getall()
        #chapter_foreword_text =
        chapter_afterword_text = response.xpath('//div[@id="novel_color"]/div[@id="novel_a"]/p/text()').getall()

        #concat all the text into 1 string
        chapter = "".join(response.xpath('//div[@id="novel_color"]/div[@id="novel_honbun"]/p/text()').getall())


    # def parse4(self, response):
    #
    #     page = response.url.split("/")[-2]
    #     filename = f'chapter_test-{page}.txt'
    #     with open(filename, 'wb') as f:
    #         f.write(response.body)

    # def parse3(self, response):
    #     chapter_title = response.css('.novel_subtitle::text').get()
    #
    #     novel_title_css = response.css("p.novel_title::text").get()
    #     novel_description = response.css('#novel_ex::text').get()
    #     chapter_title = response.css('.chapter_title::text').get()
    #     chapter_title = response.css('.novel_subtitle::text').get()
    #
    #     pass


    def save_text_to_file(self, chapter_text):
        text_file = open("sample.txt", "w")
        n = text_file.write(chapter_text)
        text_file.close()