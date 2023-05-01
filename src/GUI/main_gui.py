import PySimpleGUI as sg

# Define the layout for the GUI
layout = [
    [
        sg.Column(
            [
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
        ),
        sg.Column(
            [
                [
                    sg.Table(
                        values=[],
                        headings=["Name", "URL", "Range"],
                        key="table",
                        enable_events=True,
                        auto_size_columns=False,
                        right_click_menu=["", ["Delete"]],
                        col_widths=[10, 10, 10],
                    )
                ],
            ]
        ),
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

# Initialize the data list
data = []
novel_list = []

# Event loop
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == "Close":
        break
    if event == "add_button":
        name = values["name"]
        url = values["url"]
        range_val = values["range"]
        data.append([name, url, range_val])
        window["table"].update(values=data)
    if event == "delete_button":
        selected_rows = window["table"].SelectedRows
        if selected_rows:
            del data[selected_rows[0]]
            window["table"].update(values=data)
    if event == "selected_scraper_button":
        selected_rows = window["table"].SelectedRows
        if selected_rows:
            selected_data = [data[i] for i in selected_rows]
            tuple_data = tuple(selected_data[0])
            novel_list.append(tuple_data)
            window["output_text"].update(f"Selected rows: {tuple_data}")


# Close the window
window.close()