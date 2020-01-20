# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from youlaparser.items import YoulaparserItem
from scrapy.loader import ItemLoader


class YoulaSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['youla.ru']

    def __init__(self, city, section):
        super(YoulaSpider, self).__init__()
        self.main_url = f'https://youla.ru/{city}/{section}?page=%d'
        self.collection = f'{city}_{section}'.replace('/', '_')
        self.page = 1
        self.start_urls = [self.main_url % self.page]

    def parse(self, response: HtmlResponse):
        if response.xpath('//div[@class="pagination__button"]/a/@href').extract_first():
            self.page += 1
            yield response.follow(self.main_url % self.page, callback=self.parse)

        ads_urls = response.xpath('//li[@class="product_item"]/a/@href').extract()
        for url in ads_urls:
            yield response.follow(url, callback=self.parse_ads)

    @staticmethod
    def parse_ads(response: HtmlResponse):
        loader = ItemLoader(item=YoulaparserItem(), response=response)
        loader.add_xpath('data', '//script[contains(text(),"window.__YOULA_STATE__")]/text()')
        loader.add_value('url', response.url)
        yield loader.load_item()
