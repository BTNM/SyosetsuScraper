import jsonlines
import os


chapter_start_number_rest = 1
chapter_end_number_rest = 0


def read_jsonlines_file(
    novel_jsonlines_path, directory_path, novel_name, output_chapter_length=10
):
    """
    read_jsonlines_file() takes in a jsonfiles novel name dictionary,
    loops through all the dict object, split and unpack them in 10 chapters and write into text files
    """
    # ['novel_title', 'volume_title', 'chapter_number', 'chapter_title', 'chapter_foreword', 'chapter_text', 'chapter_afterword']

    main_text = ""
    global chapter_start_number_rest
    global chapter_end_number_rest
    start_chapter_number = 1
    # open <<filename>> jsonlines in read mode
    with jsonlines.open(novel_jsonlines_path, "r") as jsonlinesReader:
        for chapter in jsonlinesReader.iter(type=dict, skip_invalid=True):
            # Skip chapter content if chapter title in the skip list
            if chapter_title_skip_check(chapter):
                continue
            # save start and end chapter num to add to file text name
            if (
                int(chapter.get("chapter_number")) % output_chapter_length
                == chapter_start_number_rest
            ):
                if chapter.get("volume_title"):
                    main_text += chapter.get("volume_title") + "\n"
                start_chapter_number = chapter.get("chapter_number")
            # add chapter title to main output text and foreword and afterword if exist
            main_text += chapter.get("chapter_title") + "\n"
            if chapter.get("chapter_foreword"):
                main_text += chapter.get("chapter_foreword") + "\n"
            main_text += chapter.get("chapter_text") + "\n"
            if chapter.get("chapter_afterword"):
                main_text += chapter.get("chapter_afterword") + "\n"
            # get novel last chapter number
            chapter_last_num = chapter.get("chapter_start_end").split("/")[1]
            # Every 10 chapter save novel title, last chapter number to the text file output or rest chapter txt
            if (
                int(chapter.get("chapter_number")) % output_chapter_length
                == chapter_end_number_rest
                or chapter.get("chapter_number") == chapter_last_num
            ):
                end_chapter_number = chapter.get("chapter_number")
                novel_title = chapter.get("novel_title")
                start_end_chapter_number = (
                    start_chapter_number + "-" + end_chapter_number
                )

                novel_description = chapter.get("novel_description")
                if novel_description:
                    novel_title_description = novel_title + "\n" + novel_description
                else:
                    novel_title_description = ""
                # create name for output text files with chapter start end and limited novel title
                filename = start_end_chapter_number + " " + novel_title[0:30] + ".txt"

                # add start end chapter prefiks, novel title and description to main text
                if int(start_chapter_number) < output_chapter_length:
                    main_text = (
                        str(start_end_chapter_number)
                        + " "
                        + novel_title_description
                        + "\n"
                        + main_text
                    )
                else:
                    main_text = str(start_end_chapter_number) + " " + main_text

                # create directory for the novel if doesn't exist
                create_novel_directory(directory_path, novel_name)
                # output the main text to txt file in the directory
                save_text_to_file(directory_path, novel_name, filename, main_text)
                # After output main txt with content from start and end chapter num, refrech main_text
                main_text = ""

        jsonlinesReader.close()


def create_novel_directory(directory_path: str, novel_name: str):
    """
    Create a directory for the novel with the given name in the specified directory path.

    Args:
        directory_path (str): The path where the directory should be created.
        novel_name (str): The name of the novel.
    """
    # combines the directory path and novel name into a single path
    directory = os.path.join(directory_path, novel_name)
    # checks and creates the directory if it does not already exist
    if not os.path.exists(directory):
        os.mkdir(directory)


def save_text_to_file(
    directory_path: str, novel_name: str, filename: str, chapter_text: str
):
    """
    Save the content of chapter range to a text file in the specified directory path.
    Args:
        directory_path (str): The path where the file should be saved.
        novel_name (str): The name of the novel.
        filename (str): The name of the file to be saved.
        chapter_text (str): The content of the chapter to be saved.
    """
    # combines the directory path, novel name, and filename into a single path
    file_path = os.path.join(directory_path, novel_name, filename)
    # opens the file for writing with utf-8 encoding and writes the chapter content to the file
    text_file = open(file_path, "w", encoding="utf-8")
    n = text_file.write(chapter_text)
    text_file.close()


def chapter_title_skip_check(chapter: dict):
    """
    Check if the chapter title includes specific words that indicate it should be skipped.
    Args:
        chapter (dict): A dictionary containing the chapter data, including the chapter title and number.
    Returns:
        bool: True if the chapter title includes specific words that indicate it should be skipped, False otherwise.
    """
    skip_content_titles = ["人物紹介", "登場人物"]
    global chapter_start_number_rest
    global chapter_end_number_rest
    # iterates through each title to check if it is present in the chapter title
    for title_check in skip_content_titles:
        if title_check in chapter.get("chapter_title"):
            # Increase chapter rest number when modulo rest is equal to the rest for start chapter, else only return true
            if int(chapter.get("chapter_number")) % 10 == chapter_start_number_rest:
                chapter_start_number_rest += 1
                chapter_end_number_rest += 1

            return True  # returns True if the chapter should be skipped
    return False  # returns False if the chapter should not be skipped
