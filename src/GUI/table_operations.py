from bs4 import BeautifulSoup
import requests
import csv
import os
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Reduce the verbosity of the logs
logging.basicConfig(level=logging.INFO)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("WDM").setLevel(logging.WARNING)


# pyinstaller --onefile --hidden-import=scrapy --hidden-import=jsonlines --add-data "src;src" --add-data "src\GUI\syosetsu_icon.ico;SyosetsuScraper" --add-data "src\storage;storage" main.py
# pyinstaller --hidden-import=scrapy --hidden-import=jsonlines --add-data "src;src" --noconfirm main.py

# pyinstaller main.py --noconfirm --add-data=processing:processing --add-data=scraper:scraper --add-data=GUI:GUI --add-data=storage:storage --hidden-import=scrapy --hidden-import=jsonlines

# Something went wrong with the Ascendance of a Bookworm - Extra Story2 read_jsonLines_file
# An exception occurred: [Errno 2] No such file or directory: 'D:\\VisualStudioProjects\\SyosetsuScraper\\dist\\main\\_internal\\src\\storage\\Ascendance of a Bookworm - Extra Story2.jl'
# web scraping all novels in table finished
# ModuleNotFoundError: No module named 'src'
# [15780] Failed to execute script 'main' due to unhandled exception!


def load_table(folder_path, tablename):
    """
    Read a CSV file at the given file path and return its data as a list of lists, excluding the header.
    Args:
        filepath (str): The path of the CSV file to be read.
    Returns:
        list: The list of lists containing the CSV data, excluding the header.
    """
    data = []

    filepath = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "storage", f"{tablename}.csv")
    )

    if not os.path.exists(filepath):
        # Create the file if it doesn't exist
        with open(filepath, "w", newline="") as file:
            writer = csv.writer(file)
            # Write the header row if needed
            writer.writerow(["Name", "URL", "Range", "Latest"])
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


def export_table_csv(table: list, tablename, folder_path):
    """
    Save the content of the table to a CSV file in the specified directory path.
    Args:
        table (list): The list of lists representing the table data.
        tablename (str): The name of the CSV file.
    """

    filepath = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "storage", f"{tablename}.csv")
    )
    header = [["Name", "URL", "Range", "Latest"]]

    try:
        with open(filepath, mode="w", newline="", encoding="utf-8") as csv_file:
            # csv_writer = csv.writer(csv_file, quotechar='"', quoting=csv.QUOTE_ALL)
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(header)
            csv_writer.writerows(table)
    except IOError:
        print("Error writing to CSV file: {}".format(filepath))


def export_table_data(window, table_key, folder_path):
    table_values = window[table_key].get()
    novel_list = [row for row in table_values]
    # window["tab2_output_text"].update(f"table_data:{novel_list}")
    print(f"Export {table_key} novel list:")
    for novel in novel_list:
        print(novel)
    export_table_csv(novel_list, table_key, folder_path)


def handle_delete_button_event(window, values, scraped_table_data, history_table_data):
    if values["scraped_table"]:
        del scraped_table_data[values["scraped_table"][0]]
        window["input_table"].update(values=scraped_table_data)
        window["scraped_table"].update(values=scraped_table_data)
    elif values["history_table"]:
        del history_table_data[values["history_table"][0]]
        window["history_table"].update(values=history_table_data)


# Define the event handler for the table right-click menu
def handle_table_right_click_event(
    event, values, scraped_table_data, history_table_data, window
):
    if event == "Delete":
        # Check if any rows are selected in the table
        if values["input_table"]:
            del scraped_table_data[values["input_table"][0]]
            window["input_table"].update(values=scraped_table_data)
            window["scraped_table"].update(values=scraped_table_data)
        elif values["scraped_table"]:
            del scraped_table_data[values["scraped_table"][0]]
            window["input_table"].update(values=scraped_table_data)
            window["scraped_table"].update(values=scraped_table_data)
        elif values["history_table"]:
            del history_table_data[values["history_table"][0]]
            window["history_table"].update(values=history_table_data)


def handle_deselect_button_event(window, values):
    if values["history_table"]:
        window["history_table"].update(select_rows=[])
    if values["scraped_table"]:
        window["scraped_table"].update(select_rows=[])


def transfer_rows(
    window,
    source_table_key,
    destination_table_key,
    history_table_data,
    scraped_table_data,
):
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
            # update input_table on front page if transfer to scraped_table
            if source_table_key == "history_table":
                window["input_table"].update(values=destination_table_data)


def move_rows_up(window_table):
    # Get the selected row indexes
    selected_row = window_table.SelectedRows
    if selected_row:
        # Get the current table data
        table_data = window_table.Get()
        # Save the data of the selected row before moving
        selected_data = [table_data[i] for i in selected_row]
        for row in selected_row:
            if row > 0:
                # Swap the selected row with the row above it
                table_data[row], table_data[row - 1] = (
                    table_data[row - 1],
                    table_data[row],
                )

        # Update the table with the modified data
        window_table.Update(values=table_data)
        # Re-select the rows after updating the table
        # Check if the row data matches the previously selected data
        new_selected_rows = [
            i for i, row in enumerate(table_data) if row in selected_data
        ]
        # Update the selected rows in the table
        window_table.update(select_rows=new_selected_rows)


def move_rows_down(window_table):
    selected_row = window_table.SelectedRows  # Get the selected row indexes
    if selected_row:
        table_data = window_table.Get()
        selected_data = [table_data[i] for i in selected_row]
        for row in reversed(selected_row):
            if row < len(table_data) - 1:
                # Swap the selected row with the row below it
                table_data[row], table_data[row + 1] = (
                    table_data[row + 1],
                    table_data[row],
                )

        # Update the table with the modified data
        window_table.Update(values=table_data)
        new_selected_rows = [
            i for i, row in enumerate(table_data) if row in selected_data
        ]
        # Update the selected rows in the table
        window_table.update(select_rows=new_selected_rows)


# Custom input validation function
def is_input_valid_integer(value, field_name):
    try:
        # return int(value)
        if int(value):
            return True
    except ValueError:
        print(f"Wrong Input for {field_name}: {value} \nPlease enter a valid integer.")
        return False


def get_novel_latest_chapter(url: str):
    latest_chapter = None
    if "ncode.syosetu.com" in url:
        return get_novel_latest_chapter_ncode(url)
    elif "novel18.syosetu.com" in url:
        return get_novel_latest_chapter_nocturne(url)
    else:
        print(f"Get Novel Lastest Chapter didn't run with url={url}")
        return latest_chapter


def get_novel_latest_chapter_nocturne(url: str) -> int:
    # Set up Selenium WebDriver with headless option and logging preferences
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")  # Applicable to Windows OS only
    options.add_argument("--no-sandbox")  # Bypass OS security model
    options.add_argument(
        "--disable-dev-shm-usage"
    )  # Overcome limited resource problems
    options.add_argument("--log-level=3")  # Suppress logs
    options.add_argument("--silent")  # Additional option to suppress logs

    # Suppress DevTools logs
    options.set_capability(
        "goog:loggingPrefs", {"performance": "OFF", "browser": "OFF"}
    )

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=options
    )
    try:
        # Navigate to the URL
        driver.get(url)

        # Handle the age verification page
        if "novel18.syosetu.com" in url:
            time.sleep(2)  # Wait for the page to load
            enter_button = driver.find_element(By.ID, "yes18")
            enter_button.click()

        # Wait for the redirect to complete
        # driver.implicitly_wait(2)

        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Find the container with class "novelview_pager-last" to paginate to the latest chapter
        last_pager = soup.find("a", {"class": "novelview_pager-last"})
        logging.info(f"last_pager: {last_pager}")

        last_pager_href = None
        if last_pager:
            last_pager_href = last_pager.get("href")

        # Find container with class "index_box" if without paginate div
        index_box = soup.find("div", class_="index_box")
        # logging.info(f"last_pager_href: {last_pager_href}")

        if last_pager_href:
            driver.get(f"https://ncode.syosetu.com/{last_pager_href}")
            # driver.implicitly_wait(2)  # Wait for the page to load
            soup_last_page = BeautifulSoup(driver.page_source, "html.parser")

            novel_view_stats = soup_last_page.find(
                "div", class_="novelview_result-stats"
            ).get_text()
            stats_split = str.replace(novel_view_stats, "\xa0", " ").split(" ")
            return int(stats_split[3])
        # If there is no pagination, check the index box
        elif index_box:
            # Find all dl elements with class "novel_sublist2" inside the "index_box"
            chapter_list = index_box.find_all("dl", class_="novel_sublist2")

            if chapter_list:
                # Find the last "dl" element in the list
                last_chapter = chapter_list[-1]
                # Extract the chapter title
                chapter_title = last_chapter.find(
                    "dd", class_="subtitle"
                ).a.text.strip()
                # Extract the chapter number from the "a" element's href attribute
                latest_chapter = int(
                    last_chapter.find("dd", class_="subtitle").a["href"].split("/")[-2]
                )
                # Print the last chapter number and title
                # print(f"Last Chapter Number: {latest_chapter}")
                # print(f"Last Chapter Title: {chapter_title}")

                return latest_chapter
            else:
                print("No chapters found in the list")
    finally:
        driver.quit()


def get_novel_latest_chapter_ncode(url: str) -> int:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110"
    }

    # Send an HTTP GET request to the URL with header
    response = requests.get(url, headers=headers)

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, "html.parser")

    # Find container with class "novelview_pager-last" to paginate to latest chapter
    last_pager = soup.find("a", {"class": "novelview_pager-last"})
    logging.info(f"last_pager: {last_pager}")

    last_pager_href = None
    if last_pager:
        last_pager_href = last_pager.get("href")

    # Find container with class "index_box" if without paginate div
    index_box = soup.find("div", class_="index_box")
    logging.info(f"last_pager_href: {last_pager_href}")

    if last_pager_href:
        # https://ncode.syosetu.com/n4913gc/
        # https://novel18.syosetu.com/n4913gc/
        # ncode = url.split("/")[2] = "ncode.syosetu.com"
        baseurl = f"https://ncode.syosetu.com{last_pager_href}"
        responst_last_page = requests.get(baseurl, headers=headers)
        soup_last_page = BeautifulSoup(responst_last_page.content, "html.parser")

        novel_view_stats = soup_last_page.find(
            "div", class_="novelview_result-stats"
        ).get_text()
        # logging.debug(f"table_operations - novel_view_stats - {novel_view_stats}")
        stats_split = str.replace(novel_view_stats, "\xa0", " ").split(" ")
        # logging.debug(f"table_operations - stats_split - {stats_split}")
        return int(stats_split[3])

    # If there is no pagination, check the index box
    if index_box:
        # Find all dl elements with class "novel_sublist2" inside the "index_box"
        chapter_list = index_box.find_all("dl", class_="novel_sublist2")

        if chapter_list:
            # Find the last "dl" element in the list
            last_chapter = chapter_list[-1]
            # Extract the chapter title
            chapter_title = last_chapter.find("dd", class_="subtitle").a.text.strip()
            # Extract the chapter number from the "a" element's href attribute
            latest_chapter = int(
                last_chapter.find("dd", class_="subtitle").a["href"].split("/")[-2]
            )
            # Print the last chapter number and title
            # print(f"Last Chapter Number: {latest_chapter}")
            # print(f"Last Chapter Title: {chapter_title}")

            return latest_chapter
        else:
            print("No chapters found in the list")
    else:
        print(
            "Container with class 'novelview_pager-last' or 'index_box' not found in this novel web page"
        )
        return None
