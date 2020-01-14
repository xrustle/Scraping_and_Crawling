# -*- coding: utf-8 -*-
import scrapy


class HhSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['hh.ru']
    start_urls = ['http://hh.ru/']

    def parse(self, response):
        pass
