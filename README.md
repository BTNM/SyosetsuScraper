# Syosetsu Scraper

A small projects for web scraping novels on https://ncode.syosetu.com/ and divide the content into wanted size ranges,
to faciliate easy conversion into soundbooks with TextAloud and similar programs.


## Installation

    Install Scrapy using pip:

bash

pip install scrapy

    Clone this repository:

bash

git clone https://github.com/your-username/your-project.git

    Install any other requirements:

bash

pip install -r requirements.txt


## Usage
To run the spider:

bash
Copy code
scrapy crawl spidername
To save the scraped data to a file:

bash
Copy code
scrapy crawl spidername -o output.json
You can replace output.json with any other filename or file format supported by Scrapy, such as .csv or .xml.

Configuration
You can configure the spider's behavior by editing the spider's settings in the settings.py file. You can also define project-wide settings in this file.