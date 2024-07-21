import scrapy
from scrapy.crawler import CrawlerProcess
from multiprocessing import Process
from ..items import NovelItem
import logging
from ..custom_logging_handler import CustomLoggingHandler
import time
import os
import sys
import asyncio
from twisted.internet import asyncioreactor, reactor

# Set the SelectorEventLoop as the default event loop on Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Check if reactor is already installed
try:
    # Set the reactor to AsyncioSelectorReactor
    asyncioreactor.install()
except Exception:
    pass

# run scrapy shell to test scrapy extract which content
# scrapy shell 'https://ncode.syosetu.com/n1313ff/1/'
# Need to move inside the project directory where scrapy.cfg file exists to run the spider
# cd SyosetsuScraper/src/scraper , cd scraper
# scrapy crawl syosetsu -o test2.json
# scrapy crawl syosetsu -o testjl.jl

# Dynamically get the path to the temporary directory
if getattr(sys, "frozen", False):
    # If the script is run as a bundled executable
    tmp_dir = sys._MEIPASS
else:
    # If the script is run as a regular Python script
    tmp_dir = ""


class SyosetsuSpider(scrapy.Spider):
    name = "syosetsu"

    def __init__(self, start_chapter=None, *args, **kwargs):
        super(SyosetsuSpider, self).__init__(*args, **kwargs)
        self.start_chapter = start_chapter

    start_urls = [
        "https://ncode.syosetu.com/n8611bv/",
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
            # first chapter link example '/n1313ff/74/'
            first_chapter_link = response.xpath(
                '//dl[@class="novel_sublist2"]/dd[@class="subtitle"]/a/@href'
            )[0].get()
            # "https://ncode.syosetu.com / n1313ff / 74 /"
            split_chapter_link = first_chapter_link.split("/")
            # start_chapter = "55"
            if self.start_chapter:
                chapter_link = f"/{split_chapter_link[1]}/{self.start_chapter}/"
            else:
                chapter_link = first_chapter_link

            # get the first chapter link and pass novel desc to the parse_chapters method
            starting_page = response.urljoin(chapter_link)
            yield scrapy.Request(
                starting_page,
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
        time_start = time.perf_counter()
        # novel_description retrieved from meta dictionary, and passed to next parse_chapters
        novel_description = response.meta.get("novel_description")

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

        # Calculate the time taken to crawl the chapter
        time_end = time.perf_counter()
        crawl_time = time_end - time_start

        # Log the time taken to crawl the chapter
        self.logger.info(
            f"Crawled chapter {novel_item['chapter_number']} in {crawl_time:.2f} seconds"
        )

        next_page = response.xpath('//div[@class="novel_bn"]/a/@href')[1].get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(
                next_page,
                callback=self.parse_chapters,
                meta={"novel_description": novel_description},
            )


def run_spider_crawl(
    novelname: str,
    url: str,
    log_queue,
    start_chapter=None,
):
    """
    Runs the SyosetsuSpider crawler to scrape data from the provided `url` and saves the output to a JSON Lines file
    named `novelname`.jl.

    LOG_LEVEL can be set to 5 different levels
        CRITICAL: The highest level, indicating a critical error that may prevent the program from running.
        ERROR: Indicates a serious error that may affect the program's functionality.
        WARNING: Indicates a potential issue or something unexpected but not necessarily critical.
        INFO: Informational messages that provide details about the program's operation.
        DEBUG: The most detailed level, providing extensive information useful for debugging and development.
    """
    # Create a new CrawlerProcess object with project settings and the desired output file settings
    # jl_folder_path = os.path.join("src", "storage", f"{novelname}.jl")
    
    #logging.debug(f"scrapy_from_script - os.path.dirname(__file__): {os.path.dirname(__file__)}")
    #'D:\\VisualStudioProjects\\SyosetsuScraper\\dist\\main\\_internal\\src\\storage\\Ascendance of a Bookworm - Extra Story2.jl'
    if tmp_dir == "":
        jl_folder_path = os.path.join("storage", f"{novelname}.jl")
    else:
        jl_folder_path = os.path.join(
            # get last part of path "_internal"
            os.path.split(tmp_dir)[1],
            "storage",
            f"{novelname}.jl",
        )
    #logging.debug(f"scrapy_from_script - jl_folder_path: {jl_folder_path}")
    settings = {
        "FEEDS": {
            jl_folder_path: {"format": "jsonlines", "encoding": "utf8"},
        },
        # reduce the amount of logging output
        "LOG_LEVEL": "INFO",
    }
    # Create the custom logging handler
    custom_handler = CustomLoggingHandler(log_queue)
    # custom_handler.setLevel(logging.INFO)
    # Configure logging to use the custom logging handler
    logger = logging.getLogger()
    logger.addHandler(custom_handler)
    # Configure logging to ignore warnings
    logging.getLogger("py.warnings").setLevel(logging.ERROR)

    process = CrawlerProcess(settings=settings)
    # Run the spider with the current URL and output file settings
    process.crawl(SyosetsuSpider, start_urls=[url], start_chapter=start_chapter) #temp disable crawl
    # Start the process and wait for it to finish
    # TODO try to continue to text unpack after crawl
    #process.start()  
    
    # Start the reactor without installing signal handlers
    reactor.run(installSignalHandlers=False)



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
