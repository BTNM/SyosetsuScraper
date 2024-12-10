import scrapy
import time
import os
import sys
import logging
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
from multiprocessing import Process
from ..items import NovelItem
from ..custom_logging_handler import CustomLoggingHandler
from scrapy.utils.log import configure_logging
from twisted.internet import reactor

# from pathlib import Path

# run scrapy shell to test scrapy extract which content
# scrapy shell 'https://ncode.syosetu.com/n1313ff/1/'
# scrapy shell 'https://novel18.syosetu.com/n4913gc/'
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


# C:\Users\Bao Thien\.Bao Thien_todo.jl
# DEFAULT_FILE_PATH = Path.home().joinpath("." + Path.home().stem + "novelname.jl")


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
        logging.info("Start spider parse main_page crawl")
        # logging.info(f"Response: {response}")
        # INFO:root:Response: <200 https://ncode.syosetu.com/n4750dy/>

        soup = BeautifulSoup(response.text, "html.parser")

        main_page = soup.select_one("div#novel_ex.p-novel__summary").text
        # logging.info(f"Extracted main page summary: {main_page}")

        # print("Start crawl main page: {}".format(default_timer()))
        # main_page = response.xpath('//div[@class="p-novel__summary"]')
        if main_page is not None:
            novel_description = soup.select_one("div#novel_ex.p-novel__summary").text
            # first chapter link example '/n1313ff/74/'
            first_chapter_link = soup.select_one("div.p-eplist__sublist > a")["href"]
            # "https://ncode.syosetu.com / n1313ff / 74 /"
            novel_code = first_chapter_link.split("/")[1]
            # start_chapter = "55"
            if self.start_chapter:
                chapter_link: str = f"/{novel_code}/{self.start_chapter}/"
            else:
                chapter_link = first_chapter_link

            # get the first chapter link and pass novel desc to the parse_chapters method
            starting_page = response.urljoin(chapter_link)
            yield scrapy.Request(
                starting_page,
                callback=self.parse_chapters,
                meta={
                    "novel_description": novel_description,
                    "start_time": time.perf_counter(),
                },
            )

    def parse_chapters(self, response):
        """
        Parses the content of a single chapter and yields a NovelItem object containing the extracted information.
        Args:
            response: The response object representing a chapter's page.
        Returns:
            A NovelItem object containing the extracted information from the chapter.
        """
        soup = BeautifulSoup(response.text, "html.parser")
        # Calculate the time taken to crawl the chapter from request to end of processing
        time_start = response.meta.get("start_time")

        # novel_description retrieved from meta dictionary, and passed to next parse_chapters
        novel_description = response.meta.get("novel_description")

        novel_item = NovelItem()
        novel_item["novel_title"] = soup.select("div.c-announce-box div.c-announce a")[
            1
        ].text
        novel_item["novel_description"] = novel_description
        volume_title = soup.select_one("div.c-announce-box span")
        novel_item["volume_title"] = volume_title.text if volume_title else ""

        chapter_start_end = soup.select_one("div.p-novel__number").text
        novel_item["chapter_start_end"] = chapter_start_end
        novel_item["chapter_number"] = chapter_start_end.split("/")[0]
        novel_item["chapter_title"] = soup.select_one(
            "h1.p-novel__title.p-novel__title--rensai"
        ).text
        novel_item["chapter_foreword"] = "\n".join(
            p.text
            for p in soup.select(
                "div.p-novel__body div.js-novel-text.p-novel__text--preface p"
            )
        )
        novel_item["chapter_text"] = "\n".join(
            p.text
            for p in soup.select("div.p-novel__body div.js-novel-text.p-novel__text")[
                1
            ].select("p")
        )
        novel_item["chapter_afterword"] = "\n".join(
            p.text
            for p in soup.select(
                "div.p-novel__body div.js-novel-text.p-novel__text--afterword p"
            )
        )
        yield novel_item

        # Log the time taken to crawl the chapter
        time_end = time.perf_counter()
        crawl_time = time_end - time_start
        self.logger.info(
            f"Crawled chapter {novel_item['chapter_number']} in {crawl_time:.2f} seconds"
        )

        next_page_element = soup.select_one("div.c-pager a.c-pager__item--next")
        if next_page_element is not None:
            next_page_href = next_page_element["href"]
            next_page = response.urljoin(next_page_href)
            yield scrapy.Request(
                next_page,
                callback=self.parse_chapters,
                meta={
                    "novel_description": novel_description,
                    "start_time": time.perf_counter(),
                },
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
    # logging.debug(f"scrapy_from_script - os.path.dirname(__file__): {os.path.dirname(__file__)}")

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
    # logging.debug(f"scrapy_from_script - jl_folder_path: {jl_folder_path}")

    settings = {
        "FEEDS": {
            jl_folder_path: {"format": "jsonlines", "encoding": "utf8"},
        },
        "TELNETCONSOLE_ENABLED": False,
        # reduce the amount of logging output
        "LOG_LEVEL": "INFO",
        # "CLOSESPIDER_TIMEOUT": 10,
        # "CLOSESPIDER_TIMEOUT_NO_ITEM": 10,
    }
    # Create the custom logging handler
    custom_handler = CustomLoggingHandler(log_queue)
    # custom_handler.setLevel(logging.INFO)
    # Configure logging to use the custom logging handler
    logger = logging.getLogger()
    logger.addHandler(custom_handler)
    # Configure logging to ignore warnings
    logging.getLogger("py.warnings").setLevel(logging.ERROR)

    # TODO: if 'https://novel18.syosetu.com/n4913gc/' nocturne novel start selenium chromedriver to handle age verification
    process = CrawlerProcess(settings=settings)
    # Run the spider with the current URL and output file settings
    process.crawl(SyosetsuSpider, start_urls=[url], start_chapter=start_chapter)

    reactor.run()
    # Start the process and wait for it to finish
    process.start()

    # TODO: crawl/reactor not finish properly, so next text unpack wont starts


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
