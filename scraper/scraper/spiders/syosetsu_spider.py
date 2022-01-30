import scrapy


class SyosetsuSpider(scrapy.Spider):
    name = "syosetsu"
    start_urls = [
        'https://ncode.syosetu.com/n3436hb/1/',
        #'https://ncode.syosetu.com/n3436hb/2/',
        #'http://quotes.toscrape.com/page/1/',
        #'http://quotes.toscrape.com/page/2/',
    ]
    #run scrapy shell to test scrapy extract which content
    #scrapy shell "https://ncode.syosetu.com/n3436hb/1/"
    #Need to move inside the project directory where scrapy.cfg file exists to run the spider
    # cd SyosetsuScraper/src/scraper,


    def parse(self, response):
        #text_file = open("sample.txt", "w")
        #volume_title_text = response.xpath('//p[@class="chapter_title"]/text()').get()
        #n = text_file.write(volume_title_text)
        #text_file.close()

        for t in response.xpath('//p[@class="chapter_title"]'):
            yield {
                'title': t.get()
            }

        #filename = "test_chapter.txt"
        #with open(filename, 'wb') as output:
         ##   output.write(volume_title_text)


    def parse_5(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }


    def parse4(self, response):
        page = response.url.split("/")[-2]
        filename = f'chapter_test-{page}.txt'
        with open(filename, 'wb') as f:
            f.write(response.body)


    def novel_title_description(self, response):

        pass


    def parse2(self, response):
        #main text content
        response.xpath('//*[(@id = "novel_honbun")]').get()

        #xpath to the novel main text content #response.xpath('//body/div[@id="container"]/div[@id="novel_contents"]/div[@id="novel_color"]/div[@id="novel_honbun"]/p')
        volume_title_text = response.xpath('//p[@class="chapter_title"]/text()').get()
        novel_chapter_numbers = response.xpath('//div[@id="novel_no"]/text()').get()
        first_chapter_number, last_chapter_number = response.xpath('//div[@id="novel_no"]/text()').get().split("/")

        chapter_text = response.xpath('//div[@id="novel_color"]/div[@id="novel_honbun"]/p/text()').getall()
        #chapter_foreword_text =
        chapter_afterword_text = response.xpath('//div[@id="novel_color"]/div[@id="novel_a"]/p/text()').getall()

        #concat all the text into 1 string
        chapter = "".join(response.xpath('//div[@id="novel_color"]/div[@id="novel_honbun"]/p/text()').getall())


    def parse3(self, response):
        chapter_title = response.css('.novel_subtitle::text').get()

        #response.xpath("//*[starts-with(name(), 'h')]/following-sibling::p[1]/text()").getall()
        #//*[(@id = "L7")] | //*[(@id = "L8")] | //*[(@id = "L6")] | //*[(@id = "L5")] | //*[(@id = "L4")] | //*[(@id = "L2")] | //*[(@id = "L1")]

        #parse syosetsu css object from main page
        novel_title_xpath = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "novel_title", " " ))]/text()').get()
        novel_title_css = response.css("p.novel_title::text").get()

        novel_description = response.css('#novel_ex::text').get()
        chapter_title = response.css('.chapter_title::text').get()

        href = response.css('dl.novel_sublist2 a::attr(href)').get()
        #[a.attrib['href'] for a in response.css('a')]

        chapter_title = response.css('.novel_subtitle::text').get()

        first_line = response.xpath('//p[@id="L1"]/text()').get()

        first, end = response.xpath('//div[@id="novel_no"]/text()').get().split('/')

        # response.xpath("//*[starts-with(name(), 'h')]/following-sibling::p[1]/text()").getall()
        # //*[(@id = "L7")] | //*[(@id = "L8")] | //*[(@id = "L6")] | //*[(@id = "L5")] | //*[(@id = "L4")] | //*[(@id = "L2")] | //*[(@id = "L1")]

        pass


    def save_text_to_file(self, chapter_text):
        text_file = open("sample.txt", "w")
        n = text_file.write(chapter_text)
        text_file.close()