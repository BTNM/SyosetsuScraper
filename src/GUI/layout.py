import PySimpleGUI as sg
import os

# Initialize a list to store print output
print_output = []
# Set relative path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def create_layout(scraped_table_load_data, history_table_load_data):
    left_column_elements = [
        [
            sg.Text("Enter novel name:", size=(20, 1)),
            sg.Input(key="name", size=(30, 1)),
        ],
        [
            sg.Text("Enter novel URL", size=(20, 1)),
            sg.Input(
                key="url", default_text="https://ncode.syosetu.com/", size=(30, 1)
            ),
        ],
        [
            sg.Text("Enter novel Output Range", size=(20, 1)),
            sg.Input(key="range", default_text="10", size=(30, 1), enable_events=True),
        ],
        [
            sg.Text("Latest Chapter (Optional)", size=(20, 1)),
            sg.Input(key="latest_chapter", default_text="", size=(30, 1)),
        ],
        [
            sg.Button("Add", key="add_button"),
            sg.Button("Delete", key="delete_button"),
        ],
    ]

    middle_column_elements = [
        [
            sg.Table(
                values=scraped_table_load_data,
                headings=["Name", "URL", "Range", "Latest"],
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

    right_column_elements = [
        [
            sg.Text(
                text="Find Latest Selected Novel Chapter",
                justification="center",
                expand_x=True,
            ),
        ],
        [
            sg.Text(
                text="Novel Not Selected yet",
                key="select_novel",
                justification="center",
                expand_x=True,
            ),
        ],
        [
            sg.Text(
                text="0",
                key="max_chapter_output",
                justification="center",
                expand_x=True,
            ),
        ],
        [
            sg.Button(
                button_text="Get Latest Selected Novel Chapter",
                key="get_latest_chapter_btn",
                size=(25, 1),
                expand_x=True,
            ),
        ],
    ]

    # Define the layout for the novel scrape tab
    scrape_layout = [
        [
            sg.Column(left_column_elements),
            sg.Stretch(),
            sg.Column(middle_column_elements),
            sg.Column(right_column_elements, expand_x=True, expand_y=True),
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Button(
                "Start Selected Syosetsu Scraper",
                key="selected_scraper_button",
                pad=(10),
            ),
            sg.Input(
                key="input_starting_chapter",
                size=(5, 1),
                enable_events=True,
            ),
            sg.Text("Enter Specific Starting Chapter", auto_size_text=True),
            sg.Button("Start All Syosetsu Scraper", key="all_scraper_button", pad=(10)),
            sg.Text(
                "Enter Folder Path for output novel split text files:",
                auto_size_text=True,
                pad=(10, 0),
            ),
            sg.Input(
                key="input_folder_path",
                size=(40, 1),
            ),
            sg.FolderBrowse(
                button_text="Browse Output Folder Path",
                initial_folder="D:\LN Raw Text Files",
            ),
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
                size=(200, 10),
                key="output_terminal",
                reroute_stdout=True,
                reroute_cprint=True,
            ),
        ],
    ]

    # Define the layout for the novel history tab
    historical_layout = [
        [
            # Left scraped novel table column layout
            sg.Column(
                [
                    [
                        sg.Table(
                            values=scraped_table_load_data,
                            headings=["Name", "URL", "Range", "Latest"],
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
                        sg.Input(key="scraped_input_file_path", size=(55, 1)),
                        sg.FileBrowse(
                            button_text="Find Scraped Table",
                            # initial_folder="D:\VisualStudioProjects\SyosetsuScraper\src\storage",
                            initial_folder=os.path.join(src_path, "storage"),
                        ),
                        sg.Button("Load Scraped Table", key="load_scraped_btn"),
                    ],
                    [
                        sg.Input(key="scraped_input_folder_path", size=(40, 1)),
                        sg.FolderBrowse(
                            button_text="Browse Folder Export Scraped Table",
                            # initial_folder="D:\VisualStudioProjects\SyosetsuScraper\src",
                            initial_folder=src_path,
                        ),
                        sg.Button("Export Scraped Table", key="export_scraped_btn"),
                    ],
                ]
            ),
            # middle table buttons layout
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
                vertical_alignment="top",
                pad=15,
            ),
            # right scraped novel table column layout
            sg.Column(
                [
                    [
                        sg.Table(
                            values=history_table_load_data,
                            headings=["Name", "URL", "Range", "Latest"],
                            key="history_table",
                            select_mode="extended",
                            enable_events=True,
                            auto_size_columns=False,
                            right_click_menu=["", ["Delete"]],
                            justification="left",
                            col_widths=[30, 25, 5],
                        ),
                    ],
                    [
                        sg.Input(key="history_input_file_path", size=(55, 1)),
                        sg.FileBrowse(
                            button_text="Find History Table",
                            # initial_folder="D:\VisualStudioProjects\SyosetsuScraper\src\storage",
                            initial_folder=os.path.join(src_path, "storage"),
                        ),
                        sg.Button("Load History Table", key="load_history_btn"),
                    ],
                    [
                        sg.Input(key="history_input_folder_path", size=(40, 1)),
                        sg.FolderBrowse(
                            button_text="Browse Folder Export History Table",
                            # initial_folder="D:\VisualStudioProjects\SyosetsuScraper\src",
                            initial_folder=src_path,
                        ),
                        sg.Button("Export History Table", key="export_history_btn"),
                    ],
                ],
            ),  # end column
        ],
        [sg.HorizontalSeparator(pad=(10, 10, 10, 10))],
        [
            sg.Text("test_output_text", size=(20, 1), key="test_output_text"),
        ],
    ]

    tab1 = sg.Tab("Novel Scrape", scrape_layout)
    tab2 = sg.Tab("Novel History", historical_layout)
    layout_tab_group = [
        [sg.TabGroup([[tab1, tab2]], key="tab_group")],
        [sg.Button("Exit", key="exit_button")],
    ]

    return layout_tab_group
