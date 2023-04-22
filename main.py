from src.scraper.spiders.syosetsu_spider import *
from src.text_files_packing import *
import src.text_files_packing as packing
import os


def novel_crawler(novels_urls: list):
    # crawl the given syosetsu webpages
    run_multi_process_crawler(novels_urls)
    
    directory_output_path = os.path.normpath("G:\LN Raw Text Files")
    for novel_name, url, output_chapter_size  in novels_urls:
        #novel_name_jsonlines_path = os.path.normpath("C:\\Users\\Bao Thien\\PycharmProjects\\SyosetsuScraper\\{}.jl".format(novel_name))
        novel_jsonlines_path = os.path.normpath("G:\Visual Studio Code Projects\SyosetsuScraper\{}.jl".format(novel_name))
        
        try:
            print("Run read jsonline file and output txt files")
            packing.read_jsonlines_file(novel_jsonlines_path, directory_output_path, novel_name, output_chapter_size)
        except:
            print("Something went wrong with the read_jsonLines_file")
        else:
            # remove the jl file after finished reading the jl file
            print("Remove jsonlines files")
            remove_jl_file(novel_name)
        

def remove_jl_file(novel_name):
    novel = "{}.jl".format(novel_name)
    if os.path.exists(novel):
        os.remove(novel)


def illegal_char_in_name(foldername):
    invalid = '<>:"/\|?*'
    for char in invalid:
        if char in foldername:
            return char


def chapter_output_range(range: int=10):
    return range


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Feed the novel name and url to spider and crawl the webpages

    novels_urls = [
        ("Ascendance of a Bookworm - Extra Story", "https://ncode.syosetu.com/n4750dy/", chapter_output_range(3)),
        #("My Next Life as a Villainess - All Routes Lead to Doom!", "https://ncode.syosetu.com/n5040ce/", chapter_output_range()),
        #("Homeless Tensei ~Isekai de Jiyuu Sugiru Jikyuu Jisoku Seikatsu", "https://ncode.syosetu.com/n8162dq/", chapter_output_range()),
        #("The Magical Revolution of the Reincarnated Princess and the Genius Young Lady", "https://ncode.syosetu.com/n8558fh/", chapter_output_range(5)),
        #("Silent Witch", "https://ncode.syosetu.com/n5194gp/", chapter_output_range()),
        #("Food Travel in the Other World with Ridiculous Ability", "https://ncode.syosetu.com/n2710db/", chapter_output_range()),
        #("Frontier Lord Starts Out With a Population of 0", "https://ncode.syosetu.com/n1980en/", chapter_output_range()),
        #("Reincarnated as a Dragon’s Egg", "https://ncode.syosetu.com/n4698cv/", chapter_output_range()),
        #("Reincarnated as a Sword", "https://ncode.syosetu.com/n6006cw/", chapter_output_range()),
        #("Saving 80,000 Gold in an Another World for Retirement", "https://ncode.syosetu.com/n5529cy/", chapter_output_range()),
    ]

    # check illegal character in novel name
    for novel_name, url, output_chapter_size in novels_urls:
        check = illegal_char_in_name(novel_name)
        if check:
            print(f"Illegal character in {novel_name}: {check}")
            exit()

    output_chapter_size = 3
    novel_crawler(novels_urls)


# Press the green button in the gutter to run the script.
#if __name__ == '__main__':
#   print("Hello XYPython")
