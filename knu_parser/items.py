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
    day_of_week = scrapy.Field()
    date = scrapy.Field()
    discipline = scrapy.Field()
    lesson_number = scrapy.Field()
    audience = scrapy.Field()
    corpus_number = scrapy.Field()
    lecturer = scrapy.Field()
    added_at = scrapy.Field()
