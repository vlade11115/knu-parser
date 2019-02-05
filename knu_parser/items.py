# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class KnuParserItem(scrapy.Item):
    faculty_id = scrapy.Field()
    faculty_name = scrapy.Field()
    course_id = scrapy.Field()
    group_id = scrapy.Field()
    group_name = scrapy.Field()
