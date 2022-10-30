import jsonlines
import os


chapter_start_number_rest = 1
chapter_end_number_rest = 0

"""
    read_jsonlines_file() takes in a jsonfiles novel name dictionary,
    loops through all the dict object, split and unpack them in 10 chapters and write into text files  
"""
def read_jsonlines_file(novel_jsonlines, directory_path, novel_name, output_chapter_length):
    #['novel_title', 'volum_title', 'chapter_number', 'chapter_title', 'chapter_preword', 'chapter_text', 'chapter_afterword']

    main_text = ""
    global chapter_start_number_rest
    global chapter_end_number_rest
    start_chapter_number = 1
    #open <<filename>> jsonlines in read mode
    with jsonlines.open(novel_jsonlines, "r") as jsonlinesReader:
        for chapter in jsonlinesReader.iter(type=dict, skip_invalid=True):
            # Skip chapter content if chapter title in the skip list
            if chapter_title_skip_check(chapter):
                continue

            #save start and end chapter num to add to file text name
            if int(chapter.get("chapter_number")) % output_chapter_length == chapter_start_number_rest:
                if chapter.get("volum_title"):
                    main_text += chapter.get("volum_title") + "\n"
                start_chapter_number = chapter.get("chapter_number")

            #add chapter title to main output text and preword and afterword if exist
            main_text += chapter.get("chapter_title") + "\n"
            if chapter.get("chapter_preword"):
                main_text += chapter.get("chapter_preword") + "\n"
            main_text += chapter.get("chapter_text") + "\n"
            if chapter.get("chapter_afterword"):
                main_text += chapter.get("chapter_afterword") + "\n"

            #get novel last chapter number
            chapter_last_num = chapter.get("chapter_start_end").split("/")[1]
            #Every 10 chapter save novel title, last chapter number to the text file output or rest chapter txt
            if int(chapter.get("chapter_number")) % output_chapter_length == chapter_end_number_rest or chapter.get("chapter_number") == chapter_last_num:
                end_chapter_number = chapter.get("chapter_number")
                novel_title = chapter.get("novel_title")
                start_end_chapter_number = start_chapter_number + "-" + end_chapter_number

                novel_description = chapter.get("novel_description")
                if novel_description:
                    novel_title_description = novel_title + "\n" + novel_description
                else:
                    novel_title_description = ""
                # create name for output text files with chapter start end and limited novel title
                filename = start_end_chapter_number + " " + novel_title[0:30] + ".txt"

                #add start end chapter prefiks, novel title and description to main text
                if int(start_chapter_number) < output_chapter_length:
                    main_text = str(start_end_chapter_number) + " " + novel_title_description + "\n" + main_text
                else:
                    main_text = str(start_end_chapter_number) + " " + main_text

                #create directory for the novel if doesn't exist
                create_novel_directory(directory_path, novel_name)
                #output the main text to txt file in the directory
                save_text_to_file(directory_path, novel_name, filename, main_text)
                #After output main txt with content from start and end chapter num, refrech main_text
                main_text = ""


def create_novel_directory(directory_path, novel_name):
    """
    Create the directory folder in the given directory path for the novel with the given novel_name
    """
    # directory_path = "G:\LN Raw Text Files"
    directory = os.path.join(directory_path, novel_name)

    if not os.path.exists(directory):
        os.mkdir(directory)


def save_text_to_file(directory_path, novel_name, filename, chapter_text):
    """
    Save the chapter content into a txt file in the file path created from param
    :param directory_path:
    :param novel_name:
    :param filename:
    :param chapter_text:
    :return:
    """
    file_path = os.path.join(directory_path, novel_name, filename)

    text_file = open(file_path, "w", encoding="utf-8")
    n = text_file.write(chapter_text)
    text_file.close()


def chapter_title_skip_check(chapter):
    """
    Check if title includes the words in skip_content_titles to decide whether chapter should be skipped
    :param chapter: jsonline content given for the chapter
    :return: True if chapter includes the given words else False
    """
    skip_content_titles = ["人物紹介", "登場人物"]
    global chapter_start_number_rest
    global chapter_end_number_rest
    for title_check in skip_content_titles:
        if title_check in chapter.get("chapter_title"):
            # Increase chapter rest number when modulo rest is equal to the rest for start chapter, else only return true
            if int(chapter.get("chapter_number")) % 10 == chapter_start_number_rest:
                chapter_start_number_rest += 1
                chapter_end_number_rest += 1

            return True
    return False

