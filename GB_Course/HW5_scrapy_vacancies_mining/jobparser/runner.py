# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from jobparser import settings
from jobparser.spiders.hh import HhSpider
from jobparser.spiders.superjob import SuperjobSpider
import os

spiders = HhSpider, SuperjobSpider

if __name__ == '__main__':
    # Чистим логи для удобства дебага
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    if os.path.exists(crawler_settings.get('LOG_FILE')):
        os.remove(crawler_settings.get('LOG_FILE'))

    process = CrawlerProcess(settings=crawler_settings)
    for spider in spiders:
        process.crawl(spider)
    process.start()
