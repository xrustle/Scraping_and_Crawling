# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem
from hashlib import sha1
import json


class SuperjobSpider(scrapy.Spider):
    name = 'superjob'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vakansii/data-scientist.html?geo%5Bc%5D%5B0%5D=1']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.f-test-button-dalshe::attr(href)').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        vacancies = response.css('a._1QIBo::attr(href)').extract()

        for link in vacancies:
            yield response.follow(link, callback=self.parse_vacancy)

    @staticmethod
    def parse_vacancy(response: HtmlResponse):
        script = response.xpath('//script[@type="application/ld+json"]/text()').extract()
        script = '{' + ''.join(script).split('}{')[-1]
        data = json.loads(script)

        item = {'_id': sha1(data['url'].encode('utf-8')).hexdigest(),
                'title': data['title'],
                'company': data['hiringOrganization']['name'],
                'link': data['url'],
                'min_salary': None,
                'max_salary': None,
                'currency': None,
                'unit': None,
                'location': None}

        salary = data.get(['baseSalary'])
        if salary:
            item['currency'] = salary.get('currency')
            if 'value' in salary:
                item['min_salary'] = salary['value'].get('minValue')
                item['max_salary'] = salary['value'].get('maxValue')
                item['unit'] = salary['value'].get('unitText')

        location = data.get('jobLocation')
        if location:
            if 'address' in location:
                item['location'] = location['address'].get('streetAddress')

        yield JobparserItem(**item)
