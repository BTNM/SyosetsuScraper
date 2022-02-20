import jsonlines
import os


"""
    read_jsonlines_file() takes in a jsonfiles novel name dictionary,
    loops through all the dict object, split and unpack them in 10 chapters and write into text files  
"""
def read_jsonlines_file(novel_jsonlines, directory_path):
    #['novel_title', 'volum_title', 'chapter_number', 'chapter_title', 'chapter_preword', 'chapter_text', 'chapter_afterword']

    #with jsonlines.open('test12.jl', "r") as readline:
        #first = readline
        #novel_info = first.read()
        #main_text += novel_info.get("novel_title") + "\n"
        #main_text += novel_info.get("volum_title") + "\n"

    main_text = ""
    #open <<filename>> jsonlines in read mode
    with jsonlines.open(novel_jsonlines, "r") as jsonlinesReader:
        for chapter in jsonlinesReader.iter(type=dict, skip_invalid=True):
            #save start and end chapter num to add to file text name
            if int(chapter.get("chapter_number")) % 10 == 1:
                main_text += chapter.get("volum_title") + "\n"
                start_chapter_number = chapter.get("chapter_number")

            main_text += chapter.get("chapter_title") + "\n"
            if chapter.get("chapter_preword"):
                main_text += chapter.get("chapter_preword") + "\n"
            main_text += chapter.get("chapter_text") + "\n"
            if chapter.get("chapter_afterword"):
                main_text += chapter.get("chapter_afterword") + "\n"

            if int(chapter.get("chapter_number")) % 10 == 0:
                end_chapter_number = chapter.get("chapter_number")
                novel_title = chapter.get("novel_title")
                file_title = novel_title+ " " + start_chapter_number + "-" + end_chapter_number + ".txt"

                create_novel_directory(novel_title, directory_path)
                save_text_to_file(file_title, main_text, directory_path, novel_title)
                main_text = ""


def create_novel_directory(novel_title, directory_path):
    # textfiles_output_path = "G:\LN Raw Text Files"
    directory = os.path.join(directory_path, novel_title)

    if not os.path.exists(directory):
        os.mkdir(directory)


def save_text_to_file(file_title, chapter_text, directory_path, novel_title):
    file_path = os.path.join(directory_path, novel_title, file_title)

    text_file = open(file_path, "w", encoding="utf-8")
    n = text_file.write(chapter_text)
    text_file.close()