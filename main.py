from src.processing.scrapy_from_script import *
import PySimpleGUI as sg
import threading
import multiprocessing

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
    ["Another Novel", "https://example.com", 5],
    ["Yet Another Novel", "https://example.com/another", 2],
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


# Create the window
window = sg.Window("Table Example", layout)


# Define a function to run in the background
def crawl_novels(novel_list):
    # novel_crawler(novel_list)
    run_multi_process_crawler(novel_list)


# Define a function to run the scraping process in a new process
def start_scraping_process(urls):
    # Start the scraping process in a new thread
    t = threading.Thread(target=crawl_novels, args=(novel_list,))
    t.start()
    progress_layout = [
        [sg.Text("Scraping in progress...")],
        [sg.ProgressBar(len(urls), orientation="h", size=(40, 20), key="progressbar")],
    ]
    progress_window = sg.Window("Progress", progress_layout)
    progress_bar = progress_window["progressbar"]
    # Update the progress bar in the progress window while the scraper is running
    while t.is_alive():
        event, values = progress_window.read(timeout=5)
        if event == sg.WIN_CLOSED:
            break
        progress_bar.update(len(urls) - len(t._args[0]))
    progress_window.close()


# Initialize the data list
table_data = novels_urls.copy()
novel_list = []

# TODO: make executable, desktop app
# TODO: a new listbox/table that stores all novels that have been added before, persistent store in text file or something
# TODO: add new window/tab or something to store old novel data
# TODO: add option to load novel_list with list of tuple with name, url, range directly
# FIXME: restructure files, main.py into new file, imported module by main_gui

# Event loop
while True:
    event, values = window.read()
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
            # processing = multiprocessing.Process(
            #     target=start_scraping_process, args=(novel_list,)
            # )
            # processing.start()
            start_scraping_process(novel_list)

    if event == "all_scraper_button":
        # get the latest values of window table
        table_values = window["table"].get()
        novel_list = [tuple(row) for row in table_values]
        window["output_text"].update(f"table_data:{novel_list}")
        # novel_crawler(novel_list)


# Close the window
window.close()
