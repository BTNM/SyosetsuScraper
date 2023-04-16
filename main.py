from scraper.scraper.spiders.syosetsu_spider import *
from scraper.text_files_packing import *
import scraper.text_files_packing as packing
import os


def novel_scrape_run(novels_urls: list, output_chapter_size: int):
    # crawl the given syosetsu webpages
    #run_multi_process_crawler(novels_urls, output_chapter_size)
    
    directory_output_path = os.path.normpath("G:\LN Raw Text Files")
    for novel_name, url in novels_urls:
        #novel_name_jsonlines_path = os.path.normpath("C:\\Users\\Bao Thien\\PycharmProjects\\SyosetsuScraper\\{}.jl".format(novel_name))
        novel_jsonlines_path = os.path.normpath("G:\Visual Studio Code Projects\SyosetsuScraper\{}.jl".format(novel_name))
        
        try:
            print("read jsonline file and output txt files")
            packing.read_jsonlines_file(novel_jsonlines_path, directory_output_path, novel_name, output_chapter_size)
        except:
            print("Something went wrong with the read_jsonLines_file")
        else:
            # remove the jl file after finished reading the jl file
            print("remove jsonlines files")
            #remove_jl_file(novel_name)
        

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
    # Feed the novel name and url to spider and crawl the webpages

    novels_urls = [
        ("Ascendance of a Bookworm - Extra Story", "https://ncode.syosetu.com/n4750dy/"),
        ("Ascendance of a Bookworm", "https://ncode.syosetu.com/n4750dy/"),
        #("Homeless Tensei ~Isekai de Jiyuu Sugiru Jikyuu Jisoku Seikatsu", "https://ncode.syosetu.com/n8162dq/"),
    ]
    # novels_urls = [
    #     ("Ascendance of a Bookworm - Extra Story", "https://ncode.syosetu.com/n4750dy/"),
    #     ("Homeless Tensei - Isekai de Jiyuu Sugiru Jikyuu Jisoku Seikatsu", "https://ncode.syosetu.com/n8162dq/"),
    #     ("Food Travel in the Other World with Ridiculous Ability", "https://ncode.syosetu.com/n2710db/"),
    #     ("Frontier Lord Starts Out With a Population of 0", "https://ncode.syosetu.com/n1980en/"),
    #     ("Reincarnated as a Dragon’s Egg", "https://ncode.syosetu.com/n4698cv/"),
    #     ("Reincarnated as a Sword", "https://ncode.syosetu.com/n6006cw/"),
    #     ("Saving 80,000 Gold in an Another World for Retirement", "https://ncode.syosetu.com/n5529cy/"),
    # ]


    # check illegal character in novel name
    for novel_name, url in novels_urls:
        check = illegal_char_in_name(novel_name)
        if check:
            print(f"Illegal character in {novel_name}: {check}")
            exit()

    output_chapter_size = 3
    novel_scrape_run(novels_urls, output_chapter_size)


# Press the green button in the gutter to run the script.
#if __name__ == '__main__':
#   print("Hello XYPython")
