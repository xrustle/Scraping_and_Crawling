# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from jobparser import settings
from jobparser.spiders.hh import HhSpider
from jobparser.spiders.superjob import SuperjobSpider

if __name__ == '__main__':
    # Чистим логи и базу для удобства дебага

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    # hh.ru
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(HhSpider)
    process.start()

    # superjob.ru
    # process2 = CrawlerProcess(settings=crawler_settings)
    # process2.crawl(SuperjobSpider)
    # process2.start()
