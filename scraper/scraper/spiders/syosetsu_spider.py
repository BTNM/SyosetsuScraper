import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.crawler import CrawlerProcess
from multiprocessing import Process
from scrapy.settings import Settings
from twisted.internet import reactor
from scraper.scraper.items import NovelItem
from scrapy.utils.project import get_project_settings
from timeit import default_timer
import timer
import time

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
        #print("Start crawl main page: {}".format(default_timer()))
        main_page = response.xpath('//div[@class="index_box"]')
        if main_page is not None:
            global novel_description
            novel_description = "\n".join(response.xpath('//div[@id="novel_ex"]/text()').getall())
            chapter_link = response.xpath('//dl[@class="novel_sublist2"]/dd[@class="subtitle"]/a/@href')[0].get()

            start_page = response.urljoin(chapter_link)
            yield scrapy.Request(start_page, callback=self.parse_chapters)

    
    def parse_chapters(self, response):
        # Loop parsing all chapter content
        global novel_description
        start_timer = default_timer()
        novel_item = NovelItem()

        novel_item["novel_title"] = response.xpath('//div[@class="contents1"]/a[@class="margin_r20"]/text()').get()
        novel_item["novel_description"] = novel_description
        novel_item["volume_title"] = response.xpath('//p[@class="chapter_title"]/text()').get()
        novel_item["chapter_start_end"] = response.xpath('//div[@id="novel_no"]/text()').get()
        novel_item["chapter_number"] = response.xpath('//div[@id="novel_no"]/text()').get().split("/")[0]
        novel_item["chapter_title"] = response.xpath('//p[@class="novel_subtitle"]/text()').get()
        novel_item["chapter_foreword"] = "\n".join(response.xpath('//div[@id="novel_color"]/div[@id="novel_p"]/p/text()').getall())
        novel_item["chapter_text"] = "\n".join(response.xpath('//div[@id="novel_color"]/div[@id="novel_honbun"]/p/text()').getall())
        novel_item["chapter_afterword"] = "\n".join(response.xpath('//div[@id="novel_color"]/div[@id="novel_a"]/p/text()').getall())

        yield novel_item

        end_timer = default_timer()
        print("crawl chapter {}: {}".format(response.xpath('//div[@id="novel_no"]/text()').get().split("/")[0], (end_timer-start_timer)))
        next_page = response.xpath('//div[@class="novel_bn"]/a/@href')[1].get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse_chapters)


    def parse_test(self, response):
        #character introduction - 登場人物紹介
        #get next page hreft
        # response.xpath('//div[@class="novel_bn"]/a/@href')[1].get()

        #main text content
        response.xpath('//*[(@id = "novel_honbun")]').get()
        response.xpath('//p[@class="chapter_title"]/text()').get()
        #xpath to the novel main text content #response.xpath('//body/div[@id="container"]/div[@id="novel_contents"]/div[@id="novel_color"]/div[@id="novel_honbun"]/p')
        first_chapter_number, last_chapter_number = response.xpath('//div[@id="novel_no"]/text()').get().split("/")
        chapter_text = response.xpath('//div[@id="novel_color"]/div[@id="novel_honbun"]/p/text()').getall()
        #concat all the text into 1 string
        chapter = "".join(response.xpath('//div[@id="novel_color"]/div[@id="novel_honbun"]/p/text()').getall())




def run_crawler_process_spider(novel_name: str, url: str):
    """
    Run spider crawl on given url, output into a jsonlines file
    :param novel_name:
    :param url:
    :return:
    """
    process = CrawlerProcess(settings={
        "FEEDS": {
            novel_name+ '.jl': {"format": "jsonlines", 'encoding': 'utf8'},
        },
    })
    SyosetsuSpider.start_urls = [url]

    #process = CrawlerProcess(get_project_settings())
    #start_crawl = default_timer()
    start_crawl = time.time()
    print("Start spider crawl: {}".format(start_crawl))

    process.crawl(SyosetsuSpider)
    process.start()

    #end_crawl = default_timer()
    end_crawl = time.time()
    print("Spider Crawl Novel took seconds: {} / minutes: {}".format((end_crawl - start_crawl), (end_crawl - start_crawl) / 60))


def run_spider(novelname, url):
    # Create a new CrawlerProcess object with project settings and the desired output file settings
    settings = {
        "FEEDS": {
            novelname+".jl": {"format": "jsonlines", 'encoding': 'utf8'},
        },
    }
    process = CrawlerProcess(settings)
    # Run the spider with the current URL and output file settings
    process.crawl(SyosetsuSpider, start_urls=[url])
    # Start the process and wait for it to finish
    process.start()

def run_crawler_process_spider2(novels_urls, output_chapter_size):
    for novelname, url in novels_urls:
        # creates a new crawlerprocess object for each spider and runs it in a seperate process with multiprocessing
        multiprocess = Process(target=run_spider, args=(novelname, url))
        # start spider process
        multiprocess.start()
        # called after starting each process to wait for it to finish before proceeding to the next iteration
        multiprocess.join()