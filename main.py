import src.processing.scrapy_from_script as sfs
import src.scraper.spiders.syosetsu_spider as spider
import PySimpleGUI as sg
import src.GUI.layout as layout
import src.GUI.table_operations as tabop
import multiprocessing
import threading
import re


# load data from storage file for persistent data
history_table_path = (
    "D:\VisualStudioProjects\SyosetsuScraper\src\storage\history_table.csv"
)
scraped_table_path = (
    "D:\VisualStudioProjects\SyosetsuScraper\src\storage\scraped_table.csv"
)
history_table_load_data = tabop.load_table(history_table_path)
scraped_table_load_data = tabop.load_table(scraped_table_path)

layout_tab_group = layout.create_layout(
    history_table_load_data, scraped_table_load_data
)

# Create the window
window = sg.Window("Scrape Tab Group", layout_tab_group)  # , size=(1200, 700))


def run_multiprocess_crawl(novel_list, log_queue, window, start_chapter=None):
    # run scrapy separate process for each crawl, if given start crawl at start_chapter else start from beginning
    for novelname, url, output_range in novel_list:
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
    sfs.text_output_files(novel_list, start_chapter)
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
history_table_data = history_table_load_data
scraped_table_data = scraped_table_load_data
# TODO: make executable, desktop app or
# TODO: create docker image and run with a docker container
# TODO: add a fourth column to table_data to include latest chapter at that time when scrawled or null if not crawled yet
# TODO: add check for link to check current latest chapter number for novel, maybe scrape html content table size or last element, in the novel history tab


if __name__ == "__main__":
    # Event loop
    while True:
        event, values = window.read(timeout=1000)
        if event == sg.WINDOW_CLOSED or event == "exit_button":
            # export last history and scraped table data to csv storage when exit
            tabop.export_table_data(window, "history_table")
            tabop.export_table_data(window, "scraped_table")
            break
        if event == "range":
            # Check if field input is integer
            output_range = values["range"]
            if not tabop.is_input_valid_integer(output_range, "Output Range"):
                window["range"].update("")
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
            selected_novel_list = []
            if selected_rows:
                selected_data = [history_table_data[i] for i in selected_rows]
                tuple_data = tuple(selected_data[0])
                selected_novel_list.append(tuple_data)
                window["output_terminal"].print(f"Selected rows: {tuple_data}")
                # Create multiprocessing processes for each novel web scraping in the background
                # run_multiprocess_crawl(novel_list, log_queue)
                start_chapter = values["input_starting_chapter"]
                # Run the crawling process in a separate thread
                crawling_thread = threading.Thread(
                    target=run_multiprocess_crawl,
                    args=(selected_novel_list, log_queue, window, start_chapter),
                )
                crawling_thread.start()

                if selected_data[0] not in scraped_table_data:
                    scraped_table_data.append(selected_data[0])
                    window["scraped_table"].update(values=scraped_table_data)
        if event == "all_scraper_button":
            # get the latest values of window table
            table_values = window["input_table"].get()
            novel_list = [tuple(row) for row in table_values]
            window["output_terminal"].print(f"table_data:{novel_list}")
            # run_multiprocess_crawl(novel_list, log_queue)

            # Run the crawling process in a separate thread
            crawling_thread = threading.Thread(
                target=run_multiprocess_crawl, args=(novel_list, log_queue, window)
            )
            crawling_thread.start()

            for row in table_values:
                if row not in scraped_table_data:
                    scraped_table_data.append(row)
            window["scraped_table"].update(values=scraped_table_data)
        # Handle events from the "Novel History" tab
        if event == "table_row_delete_btn":
            tabop.handle_delete_button_event(
                window, values, history_table_data, scraped_table_data
            )
        if event == "deselect_btn":
            tabop.handle_deselect_button_event(window, values)
        if event == "up_arrow_btn":
            if values["history_table"]:
                tabop.move_rows_up(window["history_table"])
            elif values["scraped_table"]:
                tabop.move_rows_up(window["scraped_table"])
        if event == "down_arrow_btn":
            if values["history_table"]:
                tabop.move_rows_down(window["history_table"])
            elif values["scraped_table"]:
                tabop.move_rows_down(window["scraped_table"])
        if event == "export_history_btn":
            tabop.export_table_data(window, "history_table")
        if event == "export_scraped_btn":
            tabop.export_table_data(window, "scraped_table")
        if event == "load_history_btn":
            file_path = values["history_filepath"]
            if file_path:
                table_data = tabop.load_table(file_path)
                history_table_data = table_data
                window["history_table"].update(values=table_data)
                window["tab2_output_text"].update(f"Selected file:{table_data}")
            else:
                print("No load history filepath found")
                window["tab2_output_text"].update(f"No load history filepath found")
        if event == "load_scraped_btn":
            file_path = values["scraped_filepath"]
            if file_path:
                table_data = tabop.load_table(file_path)
                scraped_table_data = table_data
                window["scraped_table"].update(values=table_data)
                window["tab2_output_text"].update(f"Selected file:{table_data}")
            else:
                print("No scraped history filepath found")
                window["tab2_output_text"].update(f"No scraped history filepath found")
        if event == "transfer_btn":
            if values["history_table"]:
                tabop.transfer_rows(
                    window,
                    "history_table",
                    "scraped_table",
                    history_table_data,
                    scraped_table_data,
                )
            elif values["scraped_table"]:
                tabop.transfer_rows(
                    window,
                    "scraped_table",
                    "history_table",
                    history_table_data,
                    scraped_table_data,
                )
        # Check if there are new log messages in the queue
        while not log_queue.empty():
            update_progress_bar_print_logs(window, log_queue)

    # Close the window
    window.close()
