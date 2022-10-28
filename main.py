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
    # update the crawler to feed in a dict of novelname and url, or 2 strings

    #url = 'https://ncode.syosetu.com/n6006cw/'
    #novel_name = "Reincarnated as a Sword"
    #url = 'https://ncode.syosetu.com/n6240cp/'
    #novel_name = "The Other World Con Artist's Management Techniques"
    #url = 'https://ncode.syosetu.com/n4006fe/'
    #novel_name = "I'll Become a Villainess That Will Go Down in History"
    url = 'https://ncode.syosetu.com/n2710db/'
    novel_name = "Food Travel in the Other World with Ridiculous Ability"
    #url = ''
    #novel_name = ""

    novel_list = [
        {
        "url": "",
        "novel_name": ""
        },
        {
            "url": "",
            "novel_name": ""
        },
        {
            "url": "",
            "novel_name": ""
        },
    ]

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
    output_chapter_size = 10

    try:
        read_jsonlines_file(novel_name_jsonlines_path, directory_output_path, novel_name, output_chapter_size)
    except:
        print("Something went wrong with the read_jsonLines_file")
    else:
        # remove the jl file after finished reading the jl file
        remove_jl_file(novel_name)


# Press the green button in the gutter to run the script.
#if __name__ == '__main__':
 #   print("Hello XYPython")