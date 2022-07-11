from scraper.scraper.spiders.syosetsu_spider import *
from scrapy.settings import Settings
from scraper.text_files_packing import *
import os


def get_settings(filename_text: str, url: str):
    setting = Settings()
    # settings.set('FEED_URI', 'file.txt')
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


def remove_jl_file(novel_name):
    novel = "{}.jl".format(novel_name)
    if os.path.exists(novel):
        os.remove(novel)


def illegal_char_in_name(foldername):
    invalid = '<>:"/\|?*'
    for char in invalid:
        if char in foldername:
            return char


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # relative path, current working directory - os.getcwd()
    #url = 'https://ncode.syosetu.com/n4811fg/'
    #novel_name = "TRPG Player Aims For The Strongest Build In Another World"
    #url = 'https://ncode.syosetu.com/n2834dj/'
    #novel_name = "The Reincarnated Boy’s Growth Log ~The Harder I Work The Stronger I Can Become"
    url = 'https://ncode.syosetu.com/n2267be/'
    novel_name = "Re Zero - Restarting Life from Zero in Another World"

    # add illegal character in novel name
    check = illegal_char_in_name(novel_name)
    if check:
        print("Illegal character in novel name:", check)
        exit()

    # add settings and run web crawler spider
    settings = get_settings(novel_name, url)
    run_crawl_spider(settings, url)

    # read the jl file and output the split text files
    # novel_name_jsonlines_path = 'C:\\Users\\Bao Thien\\PycharmProjects\\SyosetsuScraper\\scraper\\test_output.jl'
    novel_name_jsonlines_path = os.path.normpath("C:\\Users\\Bao Thien\\PycharmProjects\\SyosetsuScraper\\{}.jl".format(novel_name))
    directory_output_path = os.path.normpath("G:\LN Raw Text Files")
    output_chapter_size = 4
    read_jsonlines_file(novel_name_jsonlines_path, directory_output_path, novel_name, output_chapter_size)

    # remove the jl file after finished reading the jl file
    remove_jl_file(novel_name)


# Press the green button in the gutter to run the script.
#if __name__ == '__main__':
 #   print("Hello XYPython")