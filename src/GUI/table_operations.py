from bs4 import BeautifulSoup
import requests
import csv
import os


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
    # Send an HTTP GET request to the URL
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110"
    }

    # Send an HTTP GET request to the URL with header
    response = requests.get(url, headers=headers)

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the container with class "index_box"
    index_box = soup.find("div", class_="index_box")
    latest_chapter = 0
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
        print("Container with class 'index_box' not found on this novel web page")
        return None
