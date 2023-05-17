from src.processing.scrapy_from_script import *
import PySimpleGUI as sg
import threading
import multiprocessing
import queue
import subprocess

# import scrapy_from_script as script


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
    ["Ascendance of a Bookworm - Extra3", "https://ncode.syosetu.com/n4750dy/", 10],
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
            col_widths=[10, 10, 10],
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


# Create a queue for inter-thread communication
# progress_queue = queue.Queue()
# Create a queue for inter-process communication
progress_queue = multiprocessing.Queue()
# Create a queue for inter-process communication
# progress_queue = queue.Queue()

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
    run_multi_process_crawler(novel_list)

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


def start_single_crawling(novelname, url):
    run_spider_crawl(novelname, url)


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
                # Create a thread to run the crawl_novels function in the background
                # crawl_novels(novel_list)
                # t = threading.Thread(target=start_crawling, args=(novel_list,))
                # t.start()
                # start_crawling(novel_list)

                # Create and run the spider in the main thread
                novelname, url, range = tuple_data
                # run_spider_crawl(novelname, url)

                p = multiprocessing.Process(
                    target=start_single_crawling, args=(novelname, url)
                )
                p.start()
                # Optionally, you can wait for the process to finish before continuing
                p.join()

                print("spider crawl finished")
                # window["output_text"].update(f"Scrape novel {novelname} finished")

                # Run the GUI in a separate thread
                # gui_thread = threading.Thread(target=start_crawling)
                # gui_thread.start()
        if event == "all_scraper_button":
            # get the latest values of window table
            table_values = window["table"].get()
            novel_list = [tuple(row) for row in table_values]
            window["output_text"].update(f"table_data:{novel_list}")
            # novel_crawler(novel_list)

    # Close the window
    window.close()
