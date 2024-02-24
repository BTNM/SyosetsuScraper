from ..scraper.spiders.syosetsu_spider import *
from .text_files_packing import *
import os


def novel_crawler_from_script(novels_urls: list):
    check_illegal_char(novels_urls)

    # crawl the given syosetsu webpages
    run_multi_process_crawler(novels_urls)

    directory_output_path = os.path.normpath("D:\LN Raw Text Files")
    for novel_name, url, output_chapter_range, latest in novels_urls:
        # novel_name_jsonlines_path = os.path.normpath("C:\\Users\\Bao Thien\\PycharmProjects\\SyosetsuScraper\\{}.jl".format(novel_name))
        novel_jsonlines_path = os.path.normpath(
            "D:\VisualStudioProjects\SyosetsuScraper\{}.jl".format(novel_name)
        )
        try:
            print("Run read jsonline file and output txt files")
            read_jsonlines_file(
                novel_jsonlines_path,
                directory_output_path,
                novel_name,
                output_chapter_range,
            )
        except:
            print("Something went wrong with the read_jsonLines_file")
        else:
            # remove the jl file after finished reading the jl file
            print("Remove jsonlines files")
            remove_jl_file(novel_name)


def text_output_files(novels_urls: list, start_chapter=None, folder_path=None):
    check_illegal_char(novels_urls)

    # TODO: make output_path to variable to decide where to output novel text files
    if folder_path:
        directory_output_path = folder_path
    else:
        directory_output_path = os.path.normpath("D:\LN Raw Text Files")

    for novel_name, url, output_chapter_range, latest in novels_urls:
        # novel_jsonlines_path = os.path.normpath(
        #     "D:\VisualStudioProjects\SyosetsuScraper\{}.jl".format(novel_name)
        # )
        novel_jsonlines_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "storage", f"{novel_name}.jl")
        )

        try:
            # print(
            #   f"novel_jsonlines_path: {novel_jsonlines_path} ,directory_output_path: {directory_output_path}, novel_name: {novel_name}, output_chapter_range: {output_chapter_range}"
            # )
            read_jsonlines_file(
                novel_jsonlines_path,
                directory_output_path,
                novel_name,
                output_chapter_range,
                start_chapter,
            )
        except Exception as error:
            print(f"Something went wrong with the {novel_name} read_jsonLines_file")
            print("An exception occurred:", error)
        else:
            # remove the jl file after finished reading the jl file
            print(f"Remove jsonlines file {novel_name}")
            remove_jl_file(novel_name)


def remove_jl_file(novel_name: str):
    """
    Deletes a .jl file with the given name if it exists in the current directory.
    """
    # novel = "{}.jl".format(novel_name)
    novel = os.path.join("src", "storage", f"{novel_name}.jl")
    # checks if file with this name exists and deletes it
    if os.path.exists(novel):
        os.remove(novel)


def illegal_char_in_name(foldername):
    """
    Checks if a folder name contains any invalid characters.
    """
    invalid = '<>:"/\|?*'
    # iterates through each character in the list of invalid characters and returns the found invalid chars
    for char in invalid:
        if char in foldername:
            return char


def check_illegal_char(novels_urls):
    # check illegal character in novel name
    for novel_name, url, output_range, latest in novels_urls:
        check = illegal_char_in_name(novel_name)
        if check:
            print(f"Illegal character in {novel_name}: {check}")
            exit()


def output_chapter_range(range: int = 10):
    """
    Returns the input range, which defaults to 10 if no argument is given
    """
    return range


if __name__ == "__main__":
    # Feed the novel name and url to spider and crawl the webpages
    test_novels = [
        (
            "Ascendance of a Bookworm - Extra Story",
            "https://ncode.syosetu.com/n4750dy/",
            output_chapter_range(3),
        ),
        # ("My Next Life as a Villainess - All Routes Lead to Doom!", "https://ncode.syosetu.com/n5040ce/", output_chapter_range()),
        # ("Homeless Tensei ~Isekai de Jiyuu Sugiru Jikyuu Jisoku Seikatsu", "https://ncode.syosetu.com/n8162dq/", output_chapter_range()),
        # ("The Magical Revolution of the Reincarnated Princess and the Genius Young Lady", "https://ncode.syosetu.com/n8558fh/", output_chapter_range(5)),
        # ("Silent Witch", "https://ncode.syosetu.com/n5194gp/", output_chapter_range(10)),
        # ("Food Travel in the Other World with Ridiculous Ability", "https://ncode.syosetu.com/n2710db/", output_chapter_range()),
        # ("Frontier Lord Starts Out With a Population of 0", "https://ncode.syosetu.com/n1980en/", output_chapter_range()),
        # ("Reincarnated as a Dragon’s Egg", "https://ncode.syosetu.com/n4698cv/", output_chapter_range()),
        # ("Reincarnated as a Sword", "https://ncode.syosetu.com/n6006cw/", output_chapter_range()),
        # ("Saving 80,000 Gold in an Another World for Retirement", "https://ncode.syosetu.com/n5529cy/", output_chapter_range()),
    ]

    novel_crawler_from_script(test_novels)
