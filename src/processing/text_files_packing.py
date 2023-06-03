import jsonlines
import os


def read_jsonlines_file(
    novel_jsonlines_path: str,
    directory_path: str,
    novel_name: str,
    output_chapter_range: int,
):
    """
    Read a JSON lines file containing a novel content, split into sized chapters, then write each
    group of chapters to a separate text file.

    Args:
        novel_jsonlines_path (str): Path to the JSON lines file containing the novel.
        directory_path (str): Path to the directory where the text files will be saved.
        novel_name (str): Name of the novel.
        output_chapter_range (int, optional): The number of chapters to include in each output text file. Defaults to 10.
    """
    # ['novel_title', 'volume_title', 'chapter_number', 'chapter_title', 'chapter_foreword', 'chapter_text', 'chapter_afterword']

    main_text = ""
    # variable keep track of chapter num that correspond to start, end of each group of chapters
    chapter_start_modulo_rest = 1
    chapter_end_modulo_rest = 0
    output_chapter_range = int(output_chapter_range)
    # Set numbering to 1, for first group of chapters start at 1
    start_chapter_numbering = 1
    with jsonlines.open(novel_jsonlines_path, "r") as jsonlinesReader:
        for chapter in jsonlinesReader.iter(type=dict, skip_invalid=True):
            chapter_number = chapter.get("chapter_number")
            # Skip chapter content if chapter title in the skip list
            title_skip = chapter_title_skip_check(chapter)
            if title_skip:
                # Increase chapter modulo check when skip chapter, if equal to output range reset to avoid start number on skipped chapters
                if (
                    int(chapter.get("chapter_number")) % output_chapter_range
                    == chapter_start_modulo_rest
                ):
                    (
                        chapter_start_modulo_rest,
                        chapter_end_modulo_rest,
                    ) = increase_chapter_modulo_rest_check(
                        chapter_start_modulo_rest,
                        chapter_end_modulo_rest,
                        output_chapter_range,
                    )
                # continue to next loop
                continue

            # save start and end chapter num to add to file text name
            if int(chapter_number) % output_chapter_range == chapter_start_modulo_rest:
                if chapter.get("volume_title"):
                    main_text += chapter.get("volume_title") + "\n"
                start_chapter_numbering = chapter_number

            # add chapter title to main output text and foreword and afterword if exist
            main_text = add_main_text_content(chapter, main_text)

            # get last novel chapter number from the start, end list
            chapter_last_num = chapter.get("chapter_start_end").split("/")[1]
            # Every output_chapter_range chapter section and save novel title, last chapter number to the text file output
            if (
                int(chapter_number) % output_chapter_range == chapter_end_modulo_rest
                or chapter_number == chapter_last_num
            ):
                novel_title = chapter.get("novel_title")
                novel_description = chapter.get("novel_description")
                start_end_chapter_number = f"{start_chapter_numbering}-{chapter_number}"
                # add start and end chapter prefix to main text, novel title and description if first txt output
                if int(start_chapter_numbering) <= output_chapter_range:
                    main_text = f"{start_end_chapter_number} {novel_title}\n{novel_description}\n{main_text}"
                else:
                    main_text = f"{start_end_chapter_number} {main_text}"

                # create directory for the novel if doesn't exist
                create_novel_directory(directory_path, novel_name)
                # combines the directory, novel name and filename into a path, and output main text to txt file in the directory
                filename = f"{start_end_chapter_number} {novel_title[:30]}.txt"
                file_path = os.path.join(directory_path, novel_name, filename)
                output_text_to_file(file_path, main_text)
                # After output main txt with content from start and end chapter num, refrech main_text
                main_text = ""


def add_main_text_content(chapter, main_text):
    """Add the main text content of a chapter to the main output text.
    Args:
        chapter (dict): A dictionary containing the chapter information,
            including the title, foreword, main text, and afterword.
        main_text (str): The main output text that the chapter content will be added to.

    Returns:
        str: The updated main output text.
    """
    # Add the chapter title to the main output text and foreword and afterword if they exist.
    main_text += chapter.get("chapter_title") + "\n"
    if chapter.get("chapter_foreword"):
        main_text += chapter.get("chapter_foreword") + "\n"
    # add main chapter content
    main_text += chapter.get("chapter_text") + "\n"
    if chapter.get("chapter_afterword"):
        main_text += chapter.get("chapter_afterword") + "\n"

    return main_text


def increase_chapter_modulo_rest_check(
    chapter_start_modulo_rest: int,
    chapter_end_modulo_rest: int,
    output_chapter_range: int,
):
    """
    Increase chapter modulo rest check variable, if rest is equal to output_chapter_range then reset back to 0 to get correct numbering
    """
    chapter_start_modulo_rest += 1
    chapter_end_modulo_rest += 1
    #
    if chapter_start_modulo_rest == output_chapter_range:
        chapter_start_modulo_rest = 0
    if chapter_end_modulo_rest == output_chapter_range:
        chapter_end_modulo_rest = 0

    return chapter_start_modulo_rest, chapter_end_modulo_rest


def chapter_title_skip_check(chapter: dict):
    """
    Check if the chapter title includes specific words that indicate it should be skipped.
    Args:
        chapter (dict): A dictionary containing the chapter data, including the chapter title and number.

    Returns:
        bool: True if the chapter title includes specific words that indicate it should be skipped, False otherwise.
    """
    skip_content_titles = ["人物紹介", "登場人物"]
    # iterates through each title to check if it is present in the chapter title
    for title_check in skip_content_titles:
        if title_check in chapter.get("chapter_title"):
            return True  # returns True, and start end num rest if the chapter should be skipped
    return False  # returns False and start end num rest if the chapter should not be skipped


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


def output_text_to_file(file_path: str, chapter_text: str):
    """
    Save the content of chapter range to a text file in the specified directory path.
    Args:
        file_path (str): The path where where the directory, novel name and filename into a path
        chapter_text (str): The content of the chapter to be saved.
    """
    # opens the file for writing with utf-8 encoding and writes the chapter content to the file
    with open(file_path, "w", encoding="utf-8") as text_file:
        text_file.write(chapter_text)
