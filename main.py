import src.processing.scrapy_from_script as sfs
import src.scraper.spiders.syosetsu_spider as spider
import PySimpleGUI as sg
import multiprocessing
import csv
import os
from src.scraper.custom_logging_handler import CustomLoggingHandler
import logging
import threading
import queue
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
import re


# test_novels = [
#     ["Ascendance of a Bookworm - Extra Story", "https://ncode.syosetu.com/n4750dy/", 3],
#     ["Ascendance of a Bookworm - Extra2", "https://ncode.syosetu.com/n4750dy/", 5],
#     # ["Ascendance of a Bookworm - Extra3", "https://ncode.syosetu.com/n4750dy/", 10],
# ]


def load_table(filepath):
    """
    Read a CSV file at the given file path and return its data as a list of lists, excluding the header.
    Args:
        filepath (str): The path of the CSV file to be read.
    Returns:
        list: The list of lists containing the CSV data, excluding the header.
    """
    data = []
    if not os.path.exists(filepath):
        # Create the file if it doesn't exist
        with open(filepath, "w", newline="") as file:
            writer = csv.writer(file)
            # Write the header row if needed
            writer.writerow(["Name", "URL", "Range"])
    else:
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                csv_reader = csv.reader(file)
                headers = next(csv_reader)  # Skip the header
                for row in csv_reader:
                    data.append(row)
        except FileNotFoundError:
            print("File not found: {}".format(filepath))
            return []
    return data


def export_table_csv(table: list, tablename):
    """
    Save the content of the table to a CSV file in the specified directory path.
    Args:
        table (list): The list of lists representing the table data.
        tablename (str): The name of the CSV file.
    """
    file_path = "D:\VisualStudioProjects\SyosetsuScraper\src\storage\{}.csv".format(
        tablename
    )
    header = [["Name", "URL", "Range"]]

    try:
        with open(file_path, mode="w", newline="", encoding="utf-8") as csv_file:
            # csv_writer = csv.writer(csv_file, quotechar='"', quoting=csv.QUOTE_ALL)
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(header)
            csv_writer.writerows(table)
    except IOError:
        print("Error writing to CSV file: {}".format(file_path))


# load data from storage file for persistent data
history_table_path = (
    "D:\VisualStudioProjects\SyosetsuScraper\src\storage\history_table.csv"
)
scraped_table_path = (
    "D:\VisualStudioProjects\SyosetsuScraper\src\storage\scraped_table.csv"
)
history_table_load_data = load_table(history_table_path)
scraped_table_load_data = load_table(scraped_table_path)


left_column_elements = [
    [
        sg.Text("Enter novel name:", size=(20, 1)),
        sg.Input(key="name", size=(30, 1)),
    ],
    [
        sg.Text("Enter novel URL", size=(20, 1)),
        sg.Input(key="url", default_text="https://ncode.syosetu.com/", size=(30, 1)),
    ],
    [
        sg.Text("Enter novel Output Range", size=(20, 1)),
        sg.Input(key="range", default_text="10", size=(30, 1)),
    ],
    [
        sg.Button("Add", key="add_button"),
        sg.Button("Delete", key="delete_button"),
    ],
]

right_column_elements = [
    [
        sg.Table(
            values=history_table_load_data,
            headings=["Name", "URL", "Range"],
            key="input_table",
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
        sg.Stretch(),
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
    [
        sg.Text("Progress: ", key="progress_text"),
        sg.ProgressBar(
            max_value=100,
            orientation="h",
            size=(40, 20),
            key="progress_bar",
            bar_color=("Green", "White"),
        ),
    ],
    [
        sg.Multiline(
            "",
            size=(180, 10),
            key="output_terminal",
            reroute_stdout=True,
            reroute_cprint=True,
        )
    ],
]

historical_layout = [
    [
        sg.Table(
            values=history_table_load_data,
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
                    sg.Button("<-->", key="transfer_btn"),
                    sg.Stretch(),
                ],
                [
                    sg.Stretch(),
                    sg.Button("Delete", key="table_row_delete_btn"),
                    sg.Stretch(),
                ],
                [
                    sg.Stretch(),
                    sg.Button("↑", key="up_arrow_btn"),
                    sg.Stretch(),
                ],
                [
                    sg.Stretch(),
                    sg.Button("↓", key="down_arrow_btn"),
                    sg.Stretch(),
                ],
                [sg.Button("Deselect", key="deselect_btn")],
            ],
            vertical_alignment="center",
        ),
        sg.Table(
            values=scraped_table_load_data,
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
        sg.Input(key="history_filepath", size=(30, 1)),
        sg.FileBrowse(
            initial_folder="D:\VisualStudioProjects\SyosetsuScraper\src\storage"
        ),
        sg.Button("Load History Table", key="load_history_btn"),
        sg.Button("Export History Table", key="export_history_btn"),
        sg.Stretch(),
        sg.Input(key="scraped_filepath", size=(30, 1)),
        sg.FileBrowse(
            initial_folder="D:\VisualStudioProjects\SyosetsuScraper\src\storage"
        ),
        sg.Button("Load Scraped Table", key="load_scraped_btn"),
        sg.Button("Export Scraped Table", key="export_scraped_btn"),
    ],
    [sg.HorizontalSeparator(pad=(10, 10, 10, 10))],
    [sg.Text("", key="tab2_output_text")],
]

tab1 = sg.Tab("Novel Scrape", scrape_layout)
tab2 = sg.Tab("Novel History", historical_layout)
layout_tab_group = [
    [sg.TabGroup([[tab1, tab2]], key="tab_group")],
    [sg.Button("Exit", key="exit_button")],
]

# Create the window
window = sg.Window("Scrape Tab Group", layout_tab_group)  # , size=(1200, 700))


def run_multiprocess_crawl(novel_list, log_queue):
    # run scrapy separate process for each crawl
    for novelname, url, output_range in novel_list:
        # signal only open on main thread, have to run on main
        multiprocess = multiprocessing.Process(
            target=spider.run_spider_crawl, args=(novelname, url, log_queue)
        )
        multiprocess.start()
        # Optionally, you can wait for the process to finish before continuing
        multiprocess.join()

    # output all crawled content in novel_list to txt files
    sfs.text_output_files(novel_list)
    print("web scraping all novels in table finished\n")


def handle_delete_button_event(values):
    if values["history_table"]:
        del history_table_data[values["history_table"][0]]
        window["input_table"].update(values=history_table_data)
        window["history_table"].update(values=history_table_data)
    elif values["scraped_table"]:
        del scraped_table_data[values["scraped_table"][0]]
        window["scraped_table"].update(values=scraped_table_data)


def handle_deselect_button_event(values):
    if values["history_table"]:
        window["history_table"].update(select_rows=[])
    if values["scraped_table"]:
        window["scraped_table"].update(select_rows=[])


def transfer_rows(window, source_table_key, destination_table_key):
    selected_rows = window[source_table_key].SelectedRows
    if source_table_key == "history_table":
        source_table_data = history_table_data
        destination_table_data = scraped_table_data
    elif source_table_key == "scraped_table":
        source_table_data = scraped_table_data
        destination_table_data = history_table_data

    if selected_rows:
        selected_row = [source_table_data[index] for index in selected_rows]
        selected_data = selected_row[0]
        if selected_data not in destination_table_data:
            destination_table_data.append(selected_data)
            window[destination_table_key].update(values=destination_table_data)
            # update input_table on front page if transfer to history_table
            if source_table_key == "scraped_table":
                window["input_table"].update(values=destination_table_data)


def move_rows_up(window_table):
    selected_rows = window_table.SelectedRows  # Get the selected row indexes
    if selected_rows:
        table_data = window_table.Get()
        for row in selected_rows:
            if row > 0:
                # Swap the selected row with the row above it
                table_data[row], table_data[row - 1] = (
                    table_data[row - 1],
                    table_data[row],
                )

        window_table.Update(
            values=table_data
        )  # Update the table with the modified data


def move_rows_down(window_table):
    selected_rows = window_table.SelectedRows  # Get the selected row indexes
    if selected_rows:
        table_data = window_table.Get()
        for row in reversed(selected_rows):
            if row < len(table_data) - 1:
                # Swap the selected row with the row below it
                table_data[row], table_data[row + 1] = (
                    table_data[row + 1],
                    table_data[row],
                )

        window_table.Update(
            values=table_data
        )  # Update the table with the modified data


def export_table_data(table_key):
    table_values = window[table_key].get()
    novel_list = [row for row in table_values]
    window["tab2_output_text"].update(f"table_data:{novel_list}")
    export_table_csv(novel_list, table_key)


def update_progress_bar_print_logs(window, log_queue):
    log_message = log_queue.get()

    # chapter_number_match = re.search(
    #     r"'chapter_number':\s*'(\d+)'", log_message
    # )
    # chapter_number = (
    #     chapter_number_match.group(1) if chapter_number_match else ""
    # )
    chapter_start_end_match = re.search(
        r"'chapter_start_end':\s*'(\d+/\d+)'", log_message
    )
    chapter_start_end = (
        chapter_start_end_match.group(1) if chapter_start_end_match else ""
    )
    # only replace content when the crawled part shows up
    if chapter_start_end:
        # Extract total_chapters from chapter_start_end
        split_start_end_chapters = chapter_start_end.split("/")

        if len(split_start_end_chapters) == 2:
            chapter_number = split_start_end_chapters[0]
            total_chapters = split_start_end_chapters[1]

            # Update the progress bar's with current chapter number and max_value with total chapters
        window["progress_bar"].update(
            current_count=int(chapter_number), max=int(total_chapters)
        )

        # Replace the content inside the brackets with chapter_start_end
        log_message = re.sub(
            r"\{[^}]*\}",
            "'chapter_number': '"
            + chapter_number
            + "'\n'chapter_start_end': '"
            + chapter_start_end
            + "'\n'total_chapters': '"
            + total_chapters
            + "'\n",
            log_message,
        )

    window["output_terminal"].print(log_message, end="")


# Create a multiprocessing queue to store the log messages
log_queue = multiprocessing.Queue()
# Initialize the data list and table data from storage
history_table_data = history_table_load_data
scraped_table_data = scraped_table_load_data
novel_list = []
# TODO: make executable, desktop app


if __name__ == "__main__":
    # Event loop
    while True:
        event, values = window.read(timeout=1000)
        if event == sg.WINDOW_CLOSED or event == "exit_button":
            # export last history and scraped table data to csv storage when exit
            export_table_data("history_table")
            export_table_data("scraped_table")
            break
        # Handle events from the "Novel Scrape" tab
        if event == "add_button":
            name = values["name"]
            url = values["url"]
            if not url.startswith("https://ncode.syosetu.com/"):
                window["output_terminal"].write(
                    f"Only novels from syosetsu starting with 'https://ncode.syosetu.com/' allowed in URL field, Invalid URL: {url}\n"
                )
                window["url"].update("")
                continue
            range_val = values["range"]
            if not range_val.isdigit():
                window["output_terminal"].write(
                    f"Only digits allowed in range field, Invalid Range: {range_val}\n"
                )
                window["range"].update("")
                continue

            history_table_data.append([name, url, range_val])
            window["input_table"].update(values=history_table_data)
            window["history_table"].update(values=history_table_data)
        if event == "delete_button":
            selected_rows = window["input_table"].SelectedRows
            if selected_rows:
                del history_table_data[selected_rows[0]]
                window["input_table"].update(values=history_table_data)
                window["history_table"].update(values=history_table_data)
        if event == "selected_scraper_button":
            selected_rows = window["input_table"].SelectedRows
            if selected_rows:
                selected_data = [history_table_data[i] for i in selected_rows]
                tuple_data = tuple(selected_data[0])
                novel_list.append(tuple_data)
                window["output_terminal"].print(f"Selected rows: {tuple_data}")
                # Create multiprocessing processes for each novel web scraping in the background
                window["progress_text"].update(f"Progress: {selected_data[0][0]}:")
                # run_multiprocess_crawl(novel_list, log_queue)
                # Run the crawling process in a separate thread
                crawling_thread = threading.Thread(
                    target=run_multiprocess_crawl, args=(novel_list, log_queue)
                )
                crawling_thread.start()

                # sfs.text_output_files(novel_list)
                if selected_data[0] not in scraped_table_data:
                    scraped_table_data.append(selected_data[0])
                    window["scraped_table"].update(values=scraped_table_data)
        if event == "all_scraper_button":
            # get the latest values of window table
            table_values = window["input_table"].get()
            novel_list = [tuple(row) for row in table_values]
            window["output_terminal"].print(f"table_data:{novel_list}")
            # run_multiprocess_crawl(novel_list, log_queue)
            # sfs.text_output_files(novel_list)
            # Run the crawling process in a separate thread
            crawling_thread = threading.Thread(
                target=run_multiprocess_crawl, args=(novel_list, log_queue)
            )
            crawling_thread.start()

            for row in table_values:
                if row not in scraped_table_data:
                    scraped_table_data.append(row)
            window["scraped_table"].update(values=scraped_table_data)
            # window["output_terminal"].print(f"Web Scrapeing novel: {novelname} finished\n")
        # Handle events from the "Novel History" tab
        if event == "table_row_delete_btn":
            handle_delete_button_event(values)
        if event == "deselect_btn":
            handle_deselect_button_event(values)
        if event == "up_arrow_btn":
            if values["history_table"]:
                move_rows_up(window["history_table"])
            elif values["scraped_table"]:
                move_rows_up(window["scraped_table"])
        if event == "down_arrow_btn":
            if values["history_table"]:
                move_rows_down(window["history_table"])
            elif values["scraped_table"]:
                move_rows_down(window["scraped_table"])
        if event == "export_history_btn":
            export_table_data("history_table")
        if event == "export_scraped_btn":
            export_table_data("scraped_table")
        if event == "load_history_btn":
            file_path = values["history_filepath"]
            if file_path:
                table_data = load_table(file_path)
                history_table_data = table_data
                window["history_table"].update(values=table_data)
                window["tab2_output_text"].update(f"Selected file:{table_data}")
            else:
                print("No load history filepath found")
                window["tab2_output_text"].update(f"No load history filepath found")
        if event == "load_scraped_btn":
            file_path = values["scraped_filepath"]
            if file_path:
                table_data = load_table(file_path)
                scraped_table_data = table_data
                window["scraped_table"].update(values=table_data)
                window["tab2_output_text"].update(f"Selected file:{table_data}")
            else:
                print("No scraped history filepath found")
                window["tab2_output_text"].update(f"No scraped history filepath found")
        if event == "transfer_btn":
            if values["history_table"]:
                transfer_rows(window, "history_table", "scraped_table")
            elif values["scraped_table"]:
                transfer_rows(window, "scraped_table", "history_table")
        # Check if there are new log messages in the queue
        while not log_queue.empty():
            update_progress_bar_print_logs(window, log_queue)

    # Close the window
    window.close()
