# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from jobparser import settings
from jobparser.spiders.hh import HhSpider
from jobparser.spiders.superjob import SuperjobSpider
import os


if __name__ == '__main__':
    # Чистим логи для удобства дебага
    os.remove('logs.txt')

    spiders = [HhSpider]  #, SuperjobSpider

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    for spider in spiders:
        process = CrawlerProcess(settings=crawler_settings)
        process.crawl(spider)
        process.start()
