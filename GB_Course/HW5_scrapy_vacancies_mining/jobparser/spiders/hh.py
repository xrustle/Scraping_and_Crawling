# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem
from hashlib import sha1
import re


class HhSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?text=Data+scientist&area=113']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        vacancies = response.xpath('//a[@data-qa="vacancy-serp__vacancy-title"]/@href').extract()

        for link in vacancies:
            yield response.follow(link, callback=self.parse_vacancy)

    @staticmethod
    def parse_vacancy(response: HtmlResponse):
        link = response.url.split('?', maxsplit=1)[0]  # Отбрасываю параметры
        item = {'_id': sha1(link.encode('utf-8')).hexdigest(),
                'title': response.xpath('//h1[@class="header"]//text()').extract_first(),
                'company': response.xpath('//a[@class="vacancy-company-name"]//text()').extract(),
                'min_salary': response.xpath('//meta[@itemprop="minValue"]/@content').extract_first(),
                'max_salary': response.xpath('//meta[@itemprop="maxValue"]/@content').extract_first(),
                'currency': response.xpath('//meta[@itemprop="currency"]/@content').extract_first(),
                'unit': response.xpath('//meta[@itemprop="unitText"]/@content').extract_first(),
                'location': response.xpath('//span[@data-qa="vacancy-view-raw-address"]//text()').extract(),
                'link': link,
                'source': 'hh.ru'}

        item['company'] = re.sub(r'\s+', ' ', ' '.join(item['company']).strip(' '))

        if not item['max_salary']:
            item['max_salary'] = response.xpath('//span[@itemprop="baseSalary"]'
                                                '//meta[@itemprop="value"]/@content').extract_first()
        if not item['location']:  # Местоположение в разных вакансиях хранится по-разному
            item['location'] = response.xpath('//span[@itemprop="jobLocation"]/..//text()').extract()
        item['location'] = re.sub(r'\s+', ' ', ' '.join(item['location']).strip(' '))

        yield JobparserItem(**item)
