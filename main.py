# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from scraper.text_files_packing import *
import os

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #print_hi('PyCharm')
    #relative path, current working directory - os.getcwd()
    #os.listdir('C:\\Users\\Bao Thien\\PycharmProjects\\SyosetsuScraper\\scraper\\test.jl')

    novel_name_jsonlines = 'C:\\Users\\Bao Thien\\PycharmProjects\\SyosetsuScraper\\scraper\\test.jl'
    textfiles_output_path = "G:\LN Raw Text Files"

    read_jsonlines_file(novel_name_jsonlines, textfiles_output_path)

