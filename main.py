from scraper.scraper.spiders.syosetsu_spider import *
from scrapy.settings import Settings
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from scraper.text_files_packing import *
import os

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def get_settings(filename_text: str, url: str):
    settings = Settings()
    #settings.set('FEED_URI', 'file.txt')
    filename_text = filename_text + ".jl"
    settings.set('FEED_URI', filename_text)
    settings.set('FEED_FORMAT', 'jsonlines')
    return settings


custom_settings = {
    'FEED_URI': 'spider1' + '.jl',
    'FEED_FORMAT': 'jsonlines',
    'FEED_EXPORTERS': {
        'jsonlines': 'scrapy.exporters.JsonLinesItemExporter',
    },
    'FEED_EXPORT_ENCODING': 'utf-8',
}


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #print_hi('PyCharm')
    #relative path, current working directory - os.getcwd()
    #os.listdir('C:\\Users\\Bao Thien\\PycharmProjects\\SyosetsuScraper\\scraper\\test.jl')
    url = 'https://ncode.syosetu.com/n1313ff/1/'
    filename = "test_output"

    settings = get_settings(filename, url)
    run_crawl_spider(settings, url)

    #novel_name_jsonlines_path = 'C:\\Users\\Bao Thien\\PycharmProjects\\SyosetsuScraper\\scraper\\test_output.jl'
    novel_name_jsonlines_path = 'C:\\Users\\Bao Thien\\PycharmProjects\\SyosetsuScraper\\test_output.jl'
    textfiles_output_path = "G:\LN Raw Text Files"

    read_jsonlines_file(novel_name_jsonlines_path, textfiles_output_path)




