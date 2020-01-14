# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem
from hashlib import sha1
import re


class HhSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy'
                  '?area=2'
                  '&st=searchVacancy'
                  '&text=Data+scientist']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        vacancy = response.xpath('//a[@data-qa="vacancy-serp__vacancy-title"]/@href').extract()

        for link in vacancy:
            yield response.follow(link, callback=self.parse_vacancy)

    @staticmethod
    def parse_vacancy(response: HtmlResponse):
        link = response.url.split('?', maxsplit=1)[0]  # Отбрасываю параметры
        item = {'_id': sha1(link.encode('utf-8')).hexdigest(),
                'name': response.xpath('//h1[@class="header"]//text()').extract_first(),
                'company': response.xpath('//a[@class="vacancy-company-name"]//text()').extract(),
                'min_salary': response.xpath('//meta[@itemprop="minValue"]/@content').extract_first(),
                'max_salary': response.xpath('//meta[@itemprop="maxValue"]/@content').extract_first(),
                'currency': response.xpath('//meta[@itemprop="currency"]/@content').extract_first(),
                'period': response.xpath('//meta[@itemprop="unitText"]/@content').extract_first(),
                'link': link}
        item['company'] = re.sub(r'\s+', ' ', ' '.join(item['company']).strip(' '))
        yield JobparserItem(**item)
