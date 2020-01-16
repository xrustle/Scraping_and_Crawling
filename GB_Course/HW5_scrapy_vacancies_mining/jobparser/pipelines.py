# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from hashlib import sha1
import json
import re
import logging

logger = logging.getLogger(__name__)


class JobparserPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    @staticmethod
    def hh_record(item):
        link = item['link'].split('?', maxsplit=1)[0]  # Отбрасываю параметры
        rec = {
            '_id': sha1(link.encode('utf-8')).hexdigest(),
            'title': item['title'],
            'company': re.sub(r'\s+', ' ', ' '.join(item['company']).strip(' ')),
            'min_salary': item['min_salary'],
            'max_salary': item['max_salary'],
            'currency': item['currency'],
            'unit': item['unit'],
            'location': item['location'],
            'link': link,
            'source': 'hh.ru'
        }

        if not rec['max_salary']:
            rec['max_salary'] = item['salary']
        if not rec['location']:  # Местоположение в разных вакансиях хранится по-разному
            rec['location'] = item['alt_location']
        rec['location'] = re.sub(r'\s+', ' ', ' '.join(rec['location']).strip(' '))
        return rec

    @staticmethod
    def superjob_record(item):
        script = '{' + ''.join(item['script']).split('}{')[-1]
        data = json.loads(script)
        rec = {
            '_id': sha1(data['url'].encode('utf-8')).hexdigest(),
            'title': data['title'],
            'company': data['hiringOrganization']['name'],
            'max_salary': None,
            'min_salary': None,
            'currency': None,
            'unit': None,
            'location': None,
            'link': data['url'],
            'source': 'superjob.ru'
        }

        salary = data.get('baseSalary')
        if salary:
            rec['currency'] = salary.get('currency')
            if 'value' in salary:
                rec['min_salary'] = salary['value'].get('minValue')
                rec['max_salary'] = salary['value'].get('maxValue')
                rec['unit'] = salary['value'].get('unitText')

        location = data.get('jobLocation')
        if location:
            if 'address' in location:
                rec['location'] = location['address'].get('streetAddress')
        return rec

    def get_db_record(self, item, spider):
        if spider == 'hh':
            return self.hh_record(item)
        elif spider == 'superjob':
            return self.superjob_record(item)

    def process_item(self, item, spider):
        db_record = self.get_db_record(item, spider.name)
        logger.debug(db_record)
        self.db[spider.name].update_one({'_id': db_record['_id']},
                                        {'$set': db_record},
                                        upsert=True)
        return item
