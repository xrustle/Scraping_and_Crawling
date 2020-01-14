# -*- coding: utf-8 -*-
import scrapy


class SuperjobSpider(scrapy.Spider):
    name = 'superjob'
    allowed_domains = ['superjob.ru']
    start_urls = ['http://superjob.ru/']

    def parse(self, response):
        pass
