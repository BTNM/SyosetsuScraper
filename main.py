from scraper.scraper.spiders.syosetsu_spider import *
from scrapy.settings import Settings
from scraper.text_files_packing import *
import os


def get_settings(filename_text: str, url: str):
    setting = Settings()
    #settings.set('FEED_URI', 'file.txt')
    filename_text = filename_text + ".jl"
    setting.set('FEED_URI', filename_text)
    setting.set('FEED_FORMAT', 'jsonlines')
    return setting

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
    #relative path, current working directory - os.getcwd()
    url = 'https://ncode.syosetu.com/n9814fq/'
    novel_name = "The Villainous Daughter’s Butler ~I Raised Her to be Very Cute~"
    #url = 'https://ncode.syosetu.com/n8611bv/'
    #novel_name = "From Common Job Class to the Strongest in the World"

    settings = get_settings(novel_name, url)
    run_crawl_spider(settings, url)

    #novel_name_jsonlines_path = 'C:\\Users\\Bao Thien\\PycharmProjects\\SyosetsuScraper\\scraper\\test_output.jl'
    novel_name_jsonlines_path = os.path.normpath("C:\\Users\\Bao Thien\\PycharmProjects\\SyosetsuScraper\\{}.jl".format(novel_name))
    directory_output_path = os.path.normpath("G:\LN Raw Text Files")

    read_jsonlines_file(novel_name_jsonlines_path, directory_output_path, novel_name)




