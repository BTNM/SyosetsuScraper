# from src.processing.scrapy_from_script import *
import src.processing.scrapy_from_script as spider
import src.processing.text_files_packing as packing
from src.processing.scrapy_from_script import *
import PySimpleGUI as sg
import multiprocessing


test_novels = [
    ["Ascendance of a Bookworm - Extra Story", "https://ncode.syosetu.com/n4750dy/", 3],
    ["Ascendance of a Bookworm - Extra2", "https://ncode.syosetu.com/n4750dy/", 5],
    # ["Ascendance of a Bookworm - Extra3", "https://ncode.syosetu.com/n4750dy/", 10],
]


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

right_column_elements = [
    [
        sg.Table(
            values=test_novels,
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
scrape_layout = [
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
]

historical_layout = [
    [
        sg.Table(
            values=test_novels,
            headings=["Name", "URL", "Range"],
            key="history_table",
            select_mode="extended",
            enable_events=True,
            auto_size_columns=False,
            right_click_menu=["", ["Delete"]],
            justification="left",
            col_widths=[30, 25, 5],
        ),
        sg.Column(
            [
                [
                    # add stretch before and after to center vertically
                    sg.Stretch(),
                    sg.Button("<-->", key="transfer_button"),
                    sg.Stretch(),
                ],
                [
                    sg.Stretch(),
                    sg.Button("Delete", key="table_row_delete_btn"),
                    sg.Stretch(),
                ],
                [sg.Button("Deselect", key="deselect_btn")],
            ],
            vertical_alignment="center",
        ),
        sg.Table(
            values=test_novels,
            headings=["Name", "URL", "Range"],
            key="scraped_table",
            select_mode="extended",
            enable_events=True,
            auto_size_columns=False,
            right_click_menu=["", ["Delete"]],
            justification="left",
            col_widths=[30, 25, 5],
        ),
    ],
    [
        sg.Button("Load", key="load_button"),
    ],
]

tab1 = sg.Tab("Novel Scrape", scrape_layout)
tab2 = sg.Tab("Novel History", historical_layout)
layout_tab_group = [
    [sg.TabGroup([[tab1, tab2]], key="tab_group")],
    [sg.Button("Exit", key="exit_button")],
]

# Create the window
window = sg.Window("Scrape Tab Group", layout_tab_group)  # , size=(1200, 700))


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


def run_multiprocess_crawl(novel_list):
    # run scrapy separate process for each crawl
    for novelname, url, output_range in novel_list:
        # signal only open on main thread, have to run on main
        multiprocess = multiprocessing.Process(
            target=spider.run_spider_crawl, args=(novelname, url)
        )
        multiprocess.start()
        # Optionally, you can wait for the process to finish before continuing
        multiprocess.join()


def handle_delete_button_event(values):
    if values["history_table"]:
        del history_table_data[values["history_table"][0]]
        window["history_table"].update(values=history_table_data)
    elif values["scraped_table"]:
        del scraped_table_data[values["scraped_table"][0]]
        window["scraped_table"].update(values=scraped_table_data)


def handle_deselect_button_event(values):
    if values["history_table"]:
        window["history_table"].update(select_rows=[])
    elif values["scraped_table"]:
        window["scraped_table"].update(select_rows=[])


def transfer_rows(window, source_table_key, destination_table_key):
    source_table = window[source_table_key]
    destination_table = window[destination_table_key]

    selected_rows = source_table.SelectedRows  # Get the selected row indexes

    if selected_rows:
        source_data = source_table.Get()
        destination_data = destination_table.Get()

        for row in selected_rows:
            selected_row_data = source_data[row]
            if selected_row_data not in destination_data:
                destination_data.append(selected_row_data)

        destination_table.Update(destination_data)


# Initialize the data list
input_table_data = test_novels.copy()
history_table_data = test_novels.copy()
scraped_table_data = test_novels.copy()
novel_list = []

# TODO: make executable, desktop app
# TODO: a new listbox/table that stores all novels that have been added before, persistent store in text file or something
# TODO: add new window/tab or something to store old novel data


if __name__ == "__main__":
    # Event loop
    while True:
        event, values = window.read(timeout=1000)
        if event == sg.WINDOW_CLOSED or event == "exit_button":
            break

        # Handle events from the "Novel Scrape" tab
        if event == "add_button":
            name = values["name"]
            url = values["url"]
            range_val = values["range"]
            input_table_data.append([name, url, range_val])
            window["table"].update(values=input_table_data)
            # add to history table as well
            history_table_data.append([name, url, range_val])
            window["history_table"].update(values=history_table_data)
        if event == "delete_button":
            selected_rows = window["table"].SelectedRows
            if selected_rows:
                del input_table_data[selected_rows[0]]
                window["table"].update(values=input_table_data)
        if event == "selected_scraper_button":
            selected_rows = window["table"].SelectedRows
            if selected_rows:
                selected_data = [input_table_data[i] for i in selected_rows]
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
        # Handle events from the "Novel History" tab
        if event == "table_row_delete_btn":
            handle_delete_button_event(values)
        if event == "deselect_btn":
            handle_deselect_button_event(values)
        if event == "transfer_button":
            # transfer_rows(window, "history_table", "scraped_table")
            selected_rows = window["history_table"].SelectedRows
            if selected_rows:
                selected_row = [input_table_data[i] for i in selected_rows]
                selected_data = selected_row[0]
                if selected_data not in scraped_table_data:
                    scraped_table_data.append(selected_data)
                    window["scraped_table"].update(values=scraped_table_data)

    # Close the window
    window.close()
