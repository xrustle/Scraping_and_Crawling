# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class HhSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy'
                  '?area=2'
                  '&st=searchVacancy'
                  '&text=Data+scientist']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').extract_first()
        yield response.follow(next_page, callback=self.parse)

        vacancy = response.css('div.vacancy-serp '
                               'div.vacancy-serp-item '
                               'div.vacancy-serp-item__row_header '
                               'a.bloko-link::attr(href)').extract()

        for link in vacancy:
            yield response.follow(link, callback=self.parse_vacancy)

    @staticmethod
    def parse_vacancy(response: HtmlResponse):
        name = response.xpath('//h1[@class=\'header\']//span/text()').extract_first()
        salary = response.css('div.vacancy-title p.vacancy-salary::text').extract()
        yield JobparserItem(name=name, salary=salary)
