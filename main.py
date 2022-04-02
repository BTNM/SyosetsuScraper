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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # relative path, current working directory - os.getcwd()
    # url = 'https://ncode.syosetu.com/n3581fh/'
    # novel_name = "I Woke Up Piloting the Strongest Starship, so I Became a Space Mercenary"
    #url = 'https://ncode.syosetu.com/n8920ex/'
    #novel_name = "Tearmoon Empire Story"
    url = 'https://ncode.syosetu.com/n1313ff/'
    novel_name = "I’m Not Even an Otome Game Mob Character"
    # url = 'https://ncode.syosetu.com/n6621fl/'
    # novel_name = "The Undead King of the Palace of Darkness"
    # url = 'https://ncode.syosetu.com/n3729en/'
    # novel_name = "Beware of that adventurer, He is the magic king ruler of the strongest subordinates"

    # add settings and run web crawler spider
    settings = get_settings(novel_name, url)
    run_crawl_spider(settings, url)

    # read the jl file and output the split text files
    # novel_name_jsonlines_path = 'C:\\Users\\Bao Thien\\PycharmProjects\\SyosetsuScraper\\scraper\\test_output.jl'
    novel_name_jsonlines_path = os.path.normpath("C:\\Users\\Bao Thien\\PycharmProjects\\SyosetsuScraper\\{}.jl".format(novel_name))
    directory_output_path = os.path.normpath("G:\LN Raw Text Files")
    read_jsonlines_file(novel_name_jsonlines_path, directory_output_path, novel_name)

    # remove the jl file after finished reading the jl file
    remove_jl_file(novel_name)
