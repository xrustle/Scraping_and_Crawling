# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from jobparser import settings
from jobparser.spiders.hh import HhSpider
from jobparser.spiders.superjob import SuperjobSpider
import os

logfile = 'logs.txt'
spiders = HhSpider, SuperjobSpider

if __name__ == '__main__':
    # Чистим логи для удобства дебага
    if os.path.exists(logfile):
        os.remove(logfile)

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    for spider in spiders:
        process.crawl(spider)
    process.start()
