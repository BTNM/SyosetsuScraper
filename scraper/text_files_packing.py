import jsonlines
import os


"""
    read_jsonlines_file() takes in a jsonfiles novel name dictionary,
    loops through all the dict object, split and unpack them in 10 chapters and write into text files  
"""
def read_jsonlines_file(novel_jsonlines, directory_path, novel_name):
    #['novel_title', 'volum_title', 'chapter_number', 'chapter_title', 'chapter_preword', 'chapter_text', 'chapter_afterword']

    main_text = ""
    #open <<filename>> jsonlines in read mode
    with jsonlines.open(novel_jsonlines, "r") as jsonlinesReader:
        for chapter in jsonlinesReader.iter(type=dict, skip_invalid=True):
            #save start and end chapter num to add to file text name
            if int(chapter.get("chapter_number")) % 10 == 1:
                if chapter.get("volum_title"):
                    main_text += chapter.get("volum_title") + "\n"
                start_chapter_number = chapter.get("chapter_number")

            main_text += chapter.get("chapter_title") + "\n"
            if chapter.get("chapter_preword"):
                main_text += chapter.get("chapter_preword") + "\n"
            main_text += chapter.get("chapter_text") + "\n"
            if chapter.get("chapter_afterword"):
                main_text += chapter.get("chapter_afterword") + "\n"

            #Every 10 chapter save novel title, last chapter number to the text file output
            if int(chapter.get("chapter_number")) % 10 == 0:
                end_chapter_number = chapter.get("chapter_number")
                novel_title = chapter.get("novel_title")
                start_end_chapter_number = start_chapter_number + "-" + end_chapter_number
                filename = start_end_chapter_number + " " + novel_title + ".txt"

                #add start end chapter prefiks to main text
                main_text = str(start_end_chapter_number) + " " + main_text

                #create directory for the novel if doesn't exist
                #create_novel_directory(novel_title, directory_path)
                create_novel_directory(directory_path, novel_name)
                #output the main text to txt file in the directory
                save_text_to_file(directory_path, novel_name, filename, main_text)
                main_text = ""


def create_novel_directory(directory_path, novel_name):
    # directory_path = "G:\LN Raw Text Files"
    directory = os.path.normpath(os.path.join(directory_path, novel_name))

    if not os.path.exists(directory):
        os.mkdir(directory)


def save_text_to_file(directory_path, novel_name, filename, chapter_text):
    file_path = os.path.join(directory_path, novel_name, filename)

    text_file = open(file_path, "w", encoding="utf-8")
    n = text_file.write(chapter_text)
    text_file.close()
