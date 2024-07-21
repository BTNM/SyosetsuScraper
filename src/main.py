import PySimpleGUI as sg
import processing.scrapy_from_script as sfs
import scraper.spiders.syosetsu_spider as spider
import GUI.layout as layout
import GUI.table_operations as tabop
import multiprocessing
import threading
import re
import os
import sys
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Dynamically get the path to the temporary directory
if getattr(sys, "frozen", False):
    # If the script is run as a bundled executable
    tmp_dir = sys._MEIPASS
else:
    # If the script is run as a regular Python script
    tmp_dir = ""


# load data from storage file for persistent data
# standard_storage_folder_path = "D:\VisualStudioProjects\SyosetsuScraper\src\storage"
standard_storage_folder_path = os.path.abspath(
    os.path.join(tmp_dir, os.path.dirname(__file__), "storage")
)

scraped_table_load_data = tabop.load_table(
    standard_storage_folder_path, "scraped_table"
)
history_table_load_data = tabop.load_table(
    standard_storage_folder_path, "history_table"
)

layout_tab_group = layout.create_layout(
    scraped_table_load_data, history_table_load_data
)

# if tmp_dir:
#     # give the dist internal system path to crawler to output at correct location
#     standard_folder_path_jl = os.path.abspath(
#         os.path.join(tmp_dir, os.path.dirname(__file__), "src")
#     )
# else:
#     standard_folder_path_jl = os.path.join(os.path.dirname(__file__), "storage")
#     #standard_folder_path_jl = os.path.abspath(os.path.join(os.path.dirname(__file__), "storage"))

# Create the window
window = sg.Window(
    "Scrape Tab Group",
    layout_tab_group,
    # icon="D:\VisualStudioProjects\SyosetsuScraper\src\GUI\syosetsu_icon.ico",
    icon=os.path.abspath(
        os.path.join(
            tmp_dir, os.path.dirname(__file__), "src", "GUI", "syosetsu_icon.ico"
        )
    ),
    # resizable=True,
)  # , size=(1200, 700))


def run_multiprocess_crawl(
    novel_list,
    log_queue,
    window,
    start_chapter=None,
    folder_path=None,
):
    # run scrapy separate process for each crawl, if given start crawl at start_chapter else start from beginning
    for novelname, url, output_range, latest in novel_list:
        window["progress_text"].update(f"Progress: {novelname}: ")
        # signal only open on main thread, have to run on main
        multiprocess = multiprocessing.Process(
            target=spider.run_spider_crawl,
            args=(novelname, url, log_queue, start_chapter),
        )
        multiprocess.start()
        # Optionally, you can wait for the process to finish before continuing
        multiprocess.join()

    # output all crawled content in novel_list to txt files
    print(
        f"In run_multiprocess_crawl sent to text_output_files start_chapter: {start_chapter}"
    )

    sfs.text_output_files(novel_list, start_chapter, folder_path)
    print("web scraping all novels in table finished\n")


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
            + "'\n'total_chapters': '"
            + total_chapters
            + "'\n'chapter_start_end': '"
            + chapter_start_end
            + "'\n",
            log_message,
        )

    window["output_terminal"].print(log_message, end="")


# Create a multiprocessing queue to store the log messages
log_queue = multiprocessing.Queue()
# Initialize the data list and table data from storage
scraped_table_data = scraped_table_load_data
history_table_data = history_table_load_data
# TODO: make executable, desktop app or
# TODO: create docker image and run with a docker container
# TODO: fix sg.table right_click_menu Delete option
# TODO: update load_table() to use same param/func as export and relative path
# TODO: use relative path for csv storage so exe can use and export table data


if __name__ == "__main__":
    # Pyinstaller multiprocessing fix
    multiprocessing.freeze_support()

    # Event loop
    while True:
        event, values = window.read(timeout=1000)
        if event == sg.WINDOW_CLOSED or event == "exit_button":
            # export last history and scraped table data to csv storage when exit
            tabop.export_table_data(
                window, "scraped_table", standard_storage_folder_path
            )
            tabop.export_table_data(
                window, "history_table", standard_storage_folder_path
            )
            break
        if event == "range":
            # Check if field input is integer
            output_range = values["range"]
            if not tabop.is_input_valid_integer(output_range, "Output Range"):
                window["range"].update("")
        if event == "latest_chapter":
            # Check if field input is integer
            output_range = values["latest_chapter"]
            if not tabop.is_input_valid_integer(output_range, "Latest Chapter"):
                window["latest_chapter"].update("")
        if event == "input_starting_chapter":
            starting_chapter = values["input_starting_chapter"]
            if not tabop.is_input_valid_integer(starting_chapter, "Starting Chapter"):
                window["input_starting_chapter"].update("")
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
            latest_chapter = values["latest_chapter"]
            if not latest_chapter.isdigit():
                window["output_terminal"].write(
                    f"Only digits allowed in latest chapter field, Invalid latest_chapter: {latest_chapter}\n"
                )
                window["latest_chapter"].update("")
            scraped_table_data.append([name, url, range_val, latest_chapter])
            window["input_table"].update(values=scraped_table_data)
            window["scraped_table"].update(values=scraped_table_data)
        if event == "delete_button":
            selected_rows = window["input_table"].SelectedRows
            if selected_rows:
                del scraped_table_data[selected_rows[0]]
                window["input_table"].update(values=scraped_table_data)
                window["scraped_table"].update(values=scraped_table_data)
        if event == "get_latest_chapter_btn":
            selected_rows = window["input_table"].SelectedRows
            if selected_rows:
                selected_data = scraped_table_data[selected_rows[0]]
                novel_name = selected_data[0]
                novel_url = selected_data[1]
                window["select_novel"].update(novel_name)

                # get latest chapter, Update the "Latest" column for the selected row in scraped_table_data
                latest_chapter = tabop.get_novel_latest_chapter(novel_url)
                selected_data[3] = latest_chapter
                # Update the table element with the modified data
                window["max_chapter_output"].update(latest_chapter)
                window["input_table"].update(values=scraped_table_data)
                window["scraped_table"].update(values=scraped_table_data)
        if event == "selected_scraper_button":
            selected_rows = window["input_table"].SelectedRows
            selected_novel_list = []
            if selected_rows:
                # selected_data = [scraped_table_data[i] for i in selected_rows]
                selected_data = scraped_table_data[selected_rows[0]]
                tuple_data = tuple(selected_data)
                selected_novel_list.append(tuple_data)
                window["output_terminal"].print(f"Selected rows: {tuple_data}")
                # Create multiprocessing processes for each novel web scraping in the background
                start_chapter = values["input_starting_chapter"]
                output_folder = values["input_folder_path"]

                logging.info(f"selected_scraper_button output_folder: {output_folder}")
                # logging.info(
                #     f"selected_scraper_button standard_folder_path_jl: {standard_folder_path_jl}"
                # )
                # Run the crawling process in a separate thread
                crawling_thread = threading.Thread(
                    target=run_multiprocess_crawl,
                    args=(
                        selected_novel_list,
                        log_queue,
                        window,
                        start_chapter,
                        output_folder,
                    ),
                )
                crawling_thread.start()

                # after scraped novel, add to history table since already in input and scraped table
                if selected_data not in history_table_data:
                    history_table_data.append(selected_data)
                    window["history_table"].update(values=history_table_data)
        if event == "all_scraper_button":
            # get the latest values of window table
            table_values = window["input_table"].get()
            novel_list = [tuple(row) for row in table_values]
            window["output_terminal"].print(f"table_data:{novel_list}")
            output_folder = values["input_folder_path"]

            # Run the crawling process in a separate thread
            crawling_thread = threading.Thread(
                target=run_multiprocess_crawl,
                args=(
                    novel_list,
                    log_queue,
                    window,
                    None,
                    output_folder,
                ),
            )
            crawling_thread.start()

            # after scraped novel, add to history table
            for row in table_values:
                if row not in history_table_data:
                    history_table_data.append(row)
            window["history_table"].update(values=history_table_data)
        # Handle events from the "Novel History" tab
        if event == "table_row_delete_btn":
            tabop.handle_delete_button_event(
                window, values, scraped_table_data, history_table_data
            )
        else:
            tabop.handle_table_right_click_event(
                event, values, scraped_table_data, history_table_data, window
            )
        if event == "deselect_btn":
            tabop.handle_deselect_button_event(window, values)
        if event == "up_arrow_btn":
            if values["scraped_table"]:
                tabop.move_rows_up(window["scraped_table"])
            elif values["history_table"]:
                tabop.move_rows_up(window["history_table"])
        if event == "down_arrow_btn":
            if values["scraped_table"]:
                tabop.move_rows_down(window["scraped_table"])
            elif values["history_table"]:
                tabop.move_rows_down(window["history_table"])
        if event == "transfer_btn":
            if values["scraped_table"]:
                tabop.transfer_rows(
                    window,
                    "scraped_table",
                    "history_table",
                    history_table_data,
                    scraped_table_data,
                )
            elif values["history_table"]:
                tabop.transfer_rows(
                    window,
                    "history_table",
                    "scraped_table",
                    history_table_data,
                    scraped_table_data,
                )
        if event == "load_scraped_btn":
            file_path = values["scraped_input_file_path"]
            if file_path:
                table_data = tabop.load_table(file_path)
                # update table scraped table data
                scraped_table_data = table_data
                window["scraped_table"].update(values=table_data)
                window["input_table"].update(values=table_data)
                window["test_output_text"].update(f"Selected file:{table_data}")
            else:
                print("No scraped history filepath found")
                window["test_output_text"].update(f"No scraped history filepath found")
        if event == "load_history_btn":
            file_path = values["history_input_file_path"]
            if file_path:
                table_data = tabop.load_table(file_path)
                history_table_data = table_data
                window["history_table"].update(values=table_data)
                window["test_output_text"].update(f"Selected file:{table_data}")
            else:
                print("No load history filepath found")
                window["test_output_text"].update(f"No load history filepath found")
        if event == "export_scraped_btn":
            folder_path = values["scraped_input_folder_path"]
            if folder_path:
                tabop.export_table_data(window, "scraped_table", folder_path)
        if event == "export_history_btn":
            folder_path = values["history_input_folder_path"]
            if folder_path:
                tabop.export_table_data(window, "history_table", folder_path)

        # Check if there are new log messages in the queue
        while not log_queue.empty():
            update_progress_bar_print_logs(window, log_queue)

    # Close the window
    window.close()
