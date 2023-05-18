# from src.processing.scrapy_from_script import *
import src.processing.scrapy_from_script as spider
import src.processing.text_files_packing as packing
from src.processing.scrapy_from_script import *
import PySimpleGUI as sg
import multiprocessing


left_column_elements = [
    [
        sg.Text("Enter novel name:", size=(20, 1)),
        sg.Input(key="name", size=(20, 1)),
    ],
    [
        sg.Text("Enter novel URL", size=(20, 1)),
        sg.Input(key="url", size=(20, 1)),
    ],
    [
        sg.Text("Enter novel Output Range", size=(20, 1)),
        sg.Input(key="range", size=(20, 1)),
    ],
    [
        sg.Button("Add", key="add_button"),
        sg.Button("Delete", key="delete_button"),
    ],
]

novels_urls = [
    ["Ascendance of a Bookworm - Extra Story", "https://ncode.syosetu.com/n4750dy/", 3],
    ["Ascendance of a Bookworm - Extra2", "https://ncode.syosetu.com/n4750dy/", 5],
    # ["Ascendance of a Bookworm - Extra3", "https://ncode.syosetu.com/n4750dy/", 10],
]

right_column_elements = [
    [
        sg.Table(
            values=novels_urls,
            headings=["Name", "URL", "Range"],
            key="table",
            select_mode="extended",
            enable_events=True,
            auto_size_columns=False,
            right_click_menu=["", ["Delete"]],
            justification="left",
            col_widths=[30, 25, 10],
        )
    ],
]

# Define the layout for the GUI
layout = [
    [
        sg.Column(left_column_elements),
        sg.Column(right_column_elements),
    ],
    [sg.HorizontalSeparator()],
    [
        sg.Button(
            "Start Selected Syosetsu Scraper", key="selected_scraper_button", pad=(10)
        ),
        sg.Button("Start All Syosetsu Scraper", key="all_scraper_button", pad=(10)),
    ],
    [sg.Text("", key="output_text")],
    [sg.Button("Close")],
]


# Create the window
window = sg.Window("Table Example", layout)


def crawl_novels(novel_list):
    progress_layout = [
        [sg.Text("Scraping in progress...")],
        [
            [sg.Text("Scraping syosetsu novel", key="output_text")],
            [sg.Button("Close")],
        ],
    ]
    progress_window = sg.Window("Scraping progress", progress_layout)

    # run_multi_process_crawler(novel_list)
    # Start the scraping process in a new thread
    # t = threading.Thread(target=run_multi_process_crawler, args=(novel_list,))
    # t.start()
    spider.run_multi_process_crawler(novel_list)

    while True:
        event, values = progress_window.read(timeout=100)
        if event == sg.WINDOW_CLOSED or event == "Close":
            break


# def start_crawling(novel_list):
#   crawl_novels(novel_list)
testlayout = [[sg.Text("Hello, World!")], [sg.Button("Exit")]]


def start_crawling2():
    # Create and run the GUI
    window = sg.Window("My GUI", layout)
    while True:
        event, values = window.read(timeout=100)
        if event == sg.WINDOW_CLOSED or event == "Exit":
            break
    window.close()


def run_multiprocess_crawl(novel_list):
    for novelname, url, output_range in novel_list:
        # signal only open on main thread, have to run on main
        multiprocess = multiprocessing.Process(
            target=spider.run_spider_crawl, args=(novelname, url)
        )
        multiprocess.start()
        # Optionally, you can wait for the process to finish before continuing
        multiprocess.join()


# Initialize the data list
table_data = novels_urls.copy()
novel_list = []

# TODO: make executable, desktop app
# TODO: a new listbox/table that stores all novels that have been added before, persistent store in text file or something
# TODO: add new window/tab or something to store old novel data
# TODO: add option to load novel_list with list of tuple with name, url, range directly
# FIXME: restructure files, main.py into new file, imported module by main_gui

if __name__ == "__main__":
    # Event loop
    while True:
        event, values = window.read(timeout=1000)
        if event == sg.WINDOW_CLOSED or event == "Close":
            break
        if event == "add_button":
            name = values["name"]
            url = values["url"]
            range_val = values["range"]
            table_data.append([name, url, range_val])
            window["table"].update(values=table_data)
        if event == "delete_button":
            selected_rows = window["table"].SelectedRows
            if selected_rows:
                del table_data[selected_rows[0]]
                window["table"].update(values=table_data)
        if event == "selected_scraper_button":
            selected_rows = window["table"].SelectedRows
            if selected_rows:
                selected_data = [table_data[i] for i in selected_rows]
                tuple_data = tuple(selected_data[0])
                novel_list.append(tuple_data)
                window["output_text"].update(f"Selected rows: {tuple_data}")
                # Create multiprocessing processes for each novel web scraping in the background
                run_multiprocess_crawl(novel_list)

                text_output_files(novel_list)
                window["output_text"].update(
                    f"Web Scraping Novel: {selected_data[0][0]} Finished"
                )
        if event == "all_scraper_button":
            # get the latest values of window table
            table_values = window["table"].get()
            novel_list = [tuple(row) for row in table_values]
            window["output_text"].update(f"table_data:{novel_list}")
            # start_multi_crawling(novel_list)
            run_multiprocess_crawl(novel_list)

            text_output_files(novel_list)
            # window["output_text"].update(f"Web Scrapeing novel: {novelname} finished")
            print("web scraping all novels in table finished")

    # Close the window
    window.close()
