# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HHItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    company = scrapy.Field()
    min_salary = scrapy.Field()
    max_salary = scrapy.Field()
    salary = scrapy.Field()
    currency = scrapy.Field()
    unit = scrapy.Field()
    location = scrapy.Field()
    alt_location = scrapy.Field()
    link = scrapy.Field()


class SuperjobItem(scrapy.Item):
    _id = scrapy.Field()
    script = scrapy.Field()
