from scraper.scraper.spiders.syosetsu_spider import *
from scraper.text_files_packing import *
import os


def novel_scrape_run(start_url: list, novel_names: list, output_chapter_size: int):
    #global check, settings

    #run web crawler spider
    #run_crawl_spider(novel_name, url) 

    #run_crawler_process_spider(novel_name, url)
    run_crawler_process_spider2(start_url, novel_names)
    novel_name = "test_file"

    # read the jl file and output the split text files
    # novel_name_jsonlines_path = 'C:\\Users\\Bao Thien\\PycharmProjects\\SyosetsuScraper\\scraper\\test_output.jl'
    #novel_name_jsonlines_path = os.path.normpath("C:\\Users\\Bao Thien\\PycharmProjects\\SyosetsuScraper\\{}.jl".format(novel_name))
    novel_name_jsonlines_path = os.path.normpath("G:\\Visual Studio Code Projects\SyosetsuScraper\\{}.jl".format(novel_name))
    directory_output_path = os.path.normpath("G:\LN Raw Text Files")

    try:
        print("read jsonline file and output txt files")
        #read_jsonlines_file(novel_name_jsonlines_path, directory_output_path, novel_name, output_chapter_size)
    except:
        print("Something went wrong with the read_jsonLines_file")
    else:
        # remove the jl file after finished reading the jl file
        #remove_jl_file(novel_name)
        pass

def novel_scrape_run2(novels_urls, output_chapter_size: int):
    run_crawler_process_spider2(novels_urls, output_chapter_size)


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

    #start_urls = [
     #   {"url": "https://ncode.syosetu.com/n4750dy/", "novel_name": "Ascendance of a Bookworm - Extra Story"},
      #  #{"url": "https://ncode.syosetu.com/n8162dq/", "novel_name": "Ascendance Homeless Tensei - test"},
    #]
    start_urls = ['https://ncode.syosetu.com/n4750dy/','https://ncode.syosetu.com/n8162dq/']
    novel_names = ["Ascendance of a Bookworm - Extra Story", 
                   "Homeless Tensei - Isekai de Jiyuu Sugiru Jikyuu Jisoku Seikatsu"
    ]

    # novels_urls = [
    #     {"Ascendance of a Bookworm - Extra Story": "https://ncode.syosetu.com/n4750dy/"},
    # ]
    novels_urls = [
        ("Ascendance of a Bookworm - Extra Story", "https://ncode.syosetu.com/n4750dy/"),
        ("Homeless Tensei - Isekai de Jiyuu Sugiru Jikyuu Jisoku Seikatsu", "https://ncode.syosetu.com/n8162dq/")
    ]

    #url = 'https://ncode.syosetu.com/n2710db/'
    #novel_name = "Food Travel in the Other World with Ridiculous Ability"

    novel_list = [
        # {
        #     "url": "https://ncode.syosetu.com/n1980en/",
        #     "novel_name": "Frontier Lord Starts Out With a Population of 0"
        # },
        # {
        #     "url": "https://ncode.syosetu.com/n8162dq/",
        #     "novel_name": "Homeless Tensei ~Isekai de Jiyuu Sugiru Jikyuu Jisoku Seikatsu~"
        # },
        {
            "url": "https://ncode.syosetu.com/n4750dy/",
            "novel_name": "Ascendance of a Bookworm - Extra Story"
        },
        # {
        #     "url": "https://ncode.syosetu.com/n4698cv/",
        #     "novel_name": "Reincarnated as a Dragon’s Egg"
        # },
        # {
        #     "url": "https://ncode.syosetu.com/n6006cw/",
        #     "novel_name": "Reincarnated as a Sword"
        # },
        # {
        #     "url": "https://ncode.syosetu.com/n5529cy/",
        #     "novel_name": "Saving 80,000 Gold in an Another World for Retirement"
        # },
    ]

    # check illegal character in novel name
    # for url_novel in novels_urls:
    #     novel_name = url_novel.keys()
    #     check = illegal_char_in_name(novel_name)
    #     if check:
    #         print(f"Illegal character in {novel_name}: {check}")
    #         exit()
    

    output_chapter_size = 3
    #for dictionary in novel_list:
     #   novel_scrape_run(dictionary["novel_name"], dictionary["url"], output_chapter_size)
    #novel_scrape_run(start_urls, novel_names, output_chapter_size)
    novel_scrape_run2(novels_urls, output_chapter_size)

# Press the green button in the gutter to run the script.
#if __name__ == '__main__':
#   print("Hello XYPython")
