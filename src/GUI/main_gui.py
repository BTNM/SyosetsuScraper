import requests
from bs4 import BeautifulSoup

# Define the URL of the website
url = "https://ncode.syosetu.com/n8611bv/"

# # Send an HTTP GET request to the URL
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
# }

# # Send an HTTP GET request to the URL with header
# response = requests.get(url, headers=headers)

# # Parse the HTML content of the page
# soup = BeautifulSoup(response.content, "html.parser")

# # Find the container with class "index_box"
# index_box = soup.find("div", class_="index_box")

# if index_box:
#     # Find all dl elements with class "novel_sublist2" inside the "index_box"
#     chapter_list = index_box.find_all("dl", class_="novel_sublist2")

#     if chapter_list:
#         # Find the last "dl" element in the list
#         last_chapter = chapter_list[-1]

#         # Extract the chapter title
#         chapter_title = last_chapter.find("dd", class_="subtitle").a.text.strip()

#         # Extract the chapter number from the "a" element's href attribute
#         chapter_number = int(
#             last_chapter.find("dd", class_="subtitle").a["href"].split("/")[-2]
#         )

#         # Print the last chapter number and title
#         print(f"Last Chapter Number: {chapter_number}")
#         print(f"Last Chapter Title: {chapter_title}")

#     else:
#         print("No chapters found in the list")

# else:
#     print("Container with class 'index_box' not found on the page")


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
            print(f"Last Chapter Number: {latest_chapter}")
            print(f"Last Chapter Title: {chapter_title}")

            return latest_chapter
        else:
            print("No chapters found in the list")
    else:
        print("Container with class 'index_box' not found on the page")
