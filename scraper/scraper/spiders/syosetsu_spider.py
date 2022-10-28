import scrapy
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.settings import Settings
from timeit import default_timer as timer

#run scrapy shell to test scrapy extract which content
#scrapy shell 'https://ncode.syosetu.com/n1313ff/1/'
#Need to move inside the project directory where scrapy.cfg file exists to run the spider
# cd SyosetsuScraper/src/scraper , cd scraper
# scrapy crawl syosetsu -o test2.json
# scrapy crawl syosetsu -o testjl.jl

novel_description = []

class SyosetsuSpider(scrapy.Spider):
    name = "syosetsu"
    start_urls = [
        'https://ncode.syosetu.com/n1313ff/',
        #'https://ncode.syosetu.com/n3436hb/1/',
    ]

    # Parse novel main page first before parsing chapter content
    def parse(self, response):
        print("Start crawl main page: {}".format(timer()))
        main_page = response.xpath('//div[@class="index_box"]')
        if main_page is not None:
            #novel_title = response.xpath('//p[@class="novel_title"]/text()').get()
            # first_link = response.xpath('//div[@class="index_box"]/dl[@class="novel_sublist2"]/dd[@class="subtitle"]/a/@href')[0]
            global novel_description
            novel_description = "\n".join(response.xpath('//div[@id="novel_ex"]/text()').getall())
            chapter_link = response.xpath('//dl[@class="novel_sublist2"]/dd[@class="subtitle"]/a/@href')[0].get()

            start_page = response.urljoin(chapter_link)
            yield scrapy.Request(start_page, callback=self.parse_chapters)

    # Loop parsing all chapter content
    def parse_chapters(self, response):
        global novel_description
        yield {
            'novel_title': response.xpath('//div[@class="contents1"]/a[@class="margin_r20"]/text()').get(),
            'novel_description': novel_description,
            'volum_title': response.xpath('//p[@class="chapter_title"]/text()').get(),
            'chapter_start_end': response.xpath('//div[@id="novel_no"]/text()').get(),
            'chapter_number': response.xpath('//div[@id="novel_no"]/text()').get().split("/")[0],
            'chapter_title': response.xpath('//p[@class="novel_subtitle"]/text()').get(),
            'chapter_preword': "\n".join(response.xpath('//div[@id="novel_color"]/div[@id="novel_p"]/p/text()').getall()),
            'chapter_text': "\n".join(response.xpath('//div[@id="novel_color"]/div[@id="novel_honbun"]/p/text()').getall()),
            'chapter_afterword': "\n".join(response.xpath('//div[@id="novel_color"]/div[@id="novel_a"]/p/text()').getall())
        }
        print("crawl chapter {}: {}".format(response.xpath('//div[@id="novel_no"]/text()').get().split("/")[0], timer()))
        next_page = response.xpath('//div[@class="novel_bn"]/a/@href')[1].get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse_chapters)


    def parse_test(self, response):
        #character introduction - 登場人物紹介

        #get next page hreft
        # response.xpath('//div[@class="novel_bn"]/a/@href')[1].get()

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
        chapter_preword_text = response.xpath('//div[@id="novel_color"]/div[@id="novel_p"]/p/text()').getall()
        chapter_afterword_text = response.xpath('//div[@id="novel_color"]/div[@id="novel_a"]/p/text()').getall()
        #concat all the text into 1 string
        chapter = "".join(response.xpath('//div[@id="novel_color"]/div[@id="novel_honbun"]/p/text()').getall())
        #css style path
        #   chapter_title = response.css('.novel_subtitle::text').get()
        #
        #   novel_title_css = response.css("p.novel_title::text").get()
        #   novel_description = response.css('#novel_ex::text').get()
        #   chapter_title = response.css('.chapter_title::text').get()
        #   chapter_title = response.css('.novel_subtitle::text').get()
        #

def run_crawl_spider(settings, url: str):
    """
    Run spider crawl on given url, output into a jsonlines file
    """
    setting = settings
    runner = CrawlerRunner(setting)
    SyosetsuSpider.start_urls = [url]

    d = runner.crawl(SyosetsuSpider)
    d.addBoth(lambda _: reactor.stop())
    start_crawl = timer()
    print("Start spider crawl: {}".format(start_crawl))
    reactor.run() # the script will block here until the crawling is finished

    end_crawl = timer()
    print("Spider Crawl Novel took seconds {} or minutes: {}".format(end_crawl, (end_crawl - start_crawl)/60))
