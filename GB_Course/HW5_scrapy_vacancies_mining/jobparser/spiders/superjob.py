# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import SuperjobItem


class SuperjobSpider(scrapy.Spider):
    name = 'superjob'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vakansii/data-scientist.html?geo%5Bc%5D%5B0%5D=1']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.f-test-button-dalshe::attr(href)').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        for link in response.css('a._1QIBo::attr(href)').extract():
            yield response.follow(link, callback=self.parse_vacancy)

    @staticmethod
    def parse_vacancy(response: HtmlResponse):
        item = {
            'script': response.xpath('//script[@type="application/ld+json"]/text()').extract()
        }
        yield SuperjobItem(**item)
