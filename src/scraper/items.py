# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NovelItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    novel_title = scrapy.Field()
    novel_description = scrapy.Field()
    volume_title = scrapy.Field()
    chapter_start_end = scrapy.Field()
    chapter_number = scrapy.Field()
    chapter_title = scrapy.Field()
    chapter_foreword = scrapy.Field()
    chapter_text = scrapy.Field()
    chapter_afterword = scrapy.Field()
