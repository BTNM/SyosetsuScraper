import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.crawler import CrawlerProcess
from multiprocessing import Process
from scrapy.settings import Settings
from twisted.internet import reactor
from src.scraper.items import NovelItem
from scrapy.utils.project import get_project_settings
from timeit import default_timer
import timer
import time

# run scrapy shell to test scrapy extract which content
# scrapy shell 'https://ncode.syosetu.com/n1313ff/1/'
# Need to move inside the project directory where scrapy.cfg file exists to run the spider
# cd SyosetsuScraper/src/scraper , cd scraper
# scrapy crawl syosetsu -o test2.json
# scrapy crawl syosetsu -o testjl.jl


class SyosetsuSpider(scrapy.Spider):
    name = "syosetsu"
    start_urls = [
        "https://ncode.syosetu.com/n1313ff/",
        #'https://ncode.syosetu.com/n3436hb/1/',
    ]

    # Parse novel main page first before parsing chapter content
    def parse(self, response):
        """
        Parses the main page of the novel and extracts the novel description and link to the first chapter.
        Args:
            response: The response object representing the main page of the novel.
        Returns:
            None. Sends a request to the first chapter's page.
        """
        # print("Start crawl main page: {}".format(default_timer()))
        main_page = response.xpath('//div[@class="index_box"]')
        if main_page is not None:
            novel_description = "\n".join(
                response.xpath('//div[@id="novel_ex"]/text()').getall()
            )
            chapter_link = response.xpath(
                '//dl[@class="novel_sublist2"]/dd[@class="subtitle"]/a/@href'
            )[0].get()
            # get the first chapter link and pass novel desc to the parse_chapters method
            start_page = response.urljoin(chapter_link)
            yield scrapy.Request(
                start_page,
                callback=self.parse_chapters,
                meta={"novel_description": novel_description},
            )

    def parse_chapters(self, response):
        """
        Parses the content of a single chapter and yields a NovelItem object containing the extracted information.
        Args:
            response: The response object representing a chapter's page.
        Returns:
            A NovelItem object containing the extracted information from the chapter.
        """
        # novel_description value is retrieved from the meta param dictionary
        novel_description = response.meta.get("novel_description")
        # start_timer = default_timer()
        novel_item = NovelItem()
        novel_item["novel_title"] = response.xpath(
            '//div[@class="contents1"]/a[@class="margin_r20"]/text()'
        ).get()
        novel_item["novel_description"] = novel_description
        novel_item["volume_title"] = response.xpath(
            '//p[@class="chapter_title"]/text()'
        ).get()
        novel_item["chapter_start_end"] = response.xpath(
            '//div[@id="novel_no"]/text()'
        ).get()
        novel_item["chapter_number"] = (
            response.xpath('//div[@id="novel_no"]/text()').get().split("/")[0]
        )
        novel_item["chapter_title"] = response.xpath(
            '//p[@class="novel_subtitle"]/text()'
        ).get()
        novel_item["chapter_foreword"] = "\n".join(
            response.xpath(
                '//div[@id="novel_color"]/div[@id="novel_p"]/p/text()'
            ).getall()
        )
        novel_item["chapter_text"] = "\n".join(
            response.xpath(
                '//div[@id="novel_color"]/div[@id="novel_honbun"]/p/text()'
            ).getall()
        )
        novel_item["chapter_afterword"] = "\n".join(
            response.xpath(
                '//div[@id="novel_color"]/div[@id="novel_a"]/p/text()'
            ).getall()
        )
        yield novel_item

        # end_timer = default_timer()
        # print("crawl chapter {}: {}".format(response.xpath('//div[@id="novel_no"]/text()').get().split("/")[0], (end_timer-start_timer)))
        next_page = response.xpath('//div[@class="novel_bn"]/a/@href')[1].get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse_chapters)

    def parse_test(self, response):
        # character introduction - 登場人物紹介
        # get next page hreft
        # response.xpath('//div[@class="novel_bn"]/a/@href')[1].get()

        # main text content
        response.xpath('//*[(@id = "novel_honbun")]').get()
        response.xpath('//p[@class="chapter_title"]/text()').get()
        # xpath to the novel main text content #response.xpath('//body/div[@id="container"]/div[@id="novel_contents"]/div[@id="novel_color"]/div[@id="novel_honbun"]/p')
        first_chapter_number, last_chapter_number = (
            response.xpath('//div[@id="novel_no"]/text()').get().split("/")
        )
        chapter_text = response.xpath(
            '//div[@id="novel_color"]/div[@id="novel_honbun"]/p/text()'
        ).getall()
        # concat all the text into 1 string
        chapter = "".join(
            response.xpath(
                '//div[@id="novel_color"]/div[@id="novel_honbun"]/p/text()'
            ).getall()
        )


def run_single_crawler_spider(novel_name: str, url: str):
    """
    Run spider crawl on given url, output into a jsonlines file
    """
    process = CrawlerProcess(
        settings={
            "FEEDS": {
                novel_name + ".jl": {"format": "jsonlines", "encoding": "utf8"},
            },
        }
    )
    SyosetsuSpider.start_urls = [url]

    # start_crawl = default_timer()
    start_crawl = time.time()
    print("Start spider crawl: {}".format(start_crawl))

    process.crawl(SyosetsuSpider)
    process.start()

    # end_crawl = default_timer()
    end_crawl = time.time()
    print(
        "Spider Crawl Novel took seconds: {} / minutes: {}".format(
            (end_crawl - start_crawl), (end_crawl - start_crawl) / 60
        )
    )


def run_spider_crawl(novelname: str, url: str):
    """
    Runs the SyosetsuSpider crawler to scrape data from the provided `url` and saves the output to a JSON Lines file
    named `novelname`.jl.
    """
    # Create a new CrawlerProcess object with project settings and the desired output file settings
    settings = {
        "FEEDS": {
            novelname + ".jl": {"format": "jsonlines", "encoding": "utf8"},
        },
        # reduce the amount of logging output
        "LOG_LEVEL": "INFO",
    }
    process = CrawlerProcess(settings=settings)
    # Run the spider with the current URL and output file settings
    process.crawl(SyosetsuSpider, start_urls=[url])
    # Start the process and wait for it to finish
    process.start()


def run_multi_process_crawler(novels_urls):
    """
    Runs multiple instances of the `run_spider_crawl` function, each in a separate process, to crawl data from
    multiple novels.

    Parameters:
    -----------
    novels_urls : list of tuples
        A list of tuples, where each tuple contains the following:
        - `novelname` : str
            The name of the novel, used for naming the output file.
        - `url` : str
            The URL of the first page to scrape.
        - `output_range` : tuple
            A tuple containing two integers, representing the range of chapters to scrape. Currently unused.
    """
    for novelname, url, output_range in novels_urls:
        # creates a new crawlerprocess object for each spider and runs it in a seperate process with multiprocessing
        multiprocess = Process(target=run_spider_crawl, args=(novelname, url))
        # start spider process
        multiprocess.start()
        # called after starting each process to wait for it to finish before proceeding to the next iteration
        multiprocess.join()
