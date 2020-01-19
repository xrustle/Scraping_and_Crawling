from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from youlaparser.spiders.youla import YoulaSpider
from youlaparser import settings
import os

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

#    if os.path.exists(crawler_settings.get('LOG_FILE')):
#        os.remove(crawler_settings.get('LOG_FILE'))

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(YoulaSpider, city='moskva', section='nedvijimost')  # nedvijimost/arenda-doma
    process.start()
