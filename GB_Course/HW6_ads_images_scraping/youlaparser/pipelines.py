# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
import scrapy
import json
import re
from hashlib import sha1
import logging

logger = logging.getLogger(__name__)


def item_path(url):
    re_search = re.search(r'^(?:[^\/]*\/){3}(.+)$', url)
    return re_search.group(1)


class ScriptParsingPipeline(object):
    def process_item(self, item, spider):
        rec = {
            'url': item['url'],
            '_id': sha1(item['url'].encode('utf-8')).hexdigest()
        }
        re_search = re.search(r'{.*}', item['data'])
        if re_search:
            item['data'] = json.loads(re_search.group(0))
            entities = item['data'].get('entities')
            if entities:
                products = entities.get('products')
                if products:
                    rec['title'] = products[0].get('name')
                    rec['description'] = products[0].get('description')

                    # Помимо записи URL изображений, также записываю путь и имя для фотографий
                    # Путь строится из URL объявления. Имя фотографии = порядковый номер + расширение из URL фотографии
                    images = products[0].get('images')
                    if images:
                        path = item_path(item['url'])
                        rec['images'] = []
                        for i, image in enumerate(images):
                            rec['images'].append({
                                image['url']: path + '/' + str(i + 1) + '.' + image['url'].split('.')[-1]})

                    location = products[0].get('location')
                    if location:
                        rec['location'] = location['description']
                    rec['price'] = products[0].get('price')
                    if rec['price']:
                        rec['price'] = rec['price'] / 100

                    # Доп. атрибуты
                    attributes = products[0].get('attributes')
                    if attributes:
                        rec['attributes'] = {}
                        for attr in attributes:
                            key = attr['slug']
                            value = attr['values'][0]['value']
                            if value.isdigit():
                                if 'price' in key or 'ploshad' in key:
                                    value = int(value) / 100
                                else:
                                    value = int(value)
                            rec['attributes'][key] = value
        item = rec
        return item


class YoulaImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        images = item.get('images')
        if images:
            for image in images:
                for image_url, img_dir in image.items():
                    request = scrapy.Request(url=image_url)
                    request.meta['img_dir'] = img_dir
                    yield request

    def file_path(self, request, response=None, info=None):
        return request.meta['img_dir']

    def item_completed(self, results, item, info):
        if results:
            item['images'] = [itm[1] for itm in results if itm[0]]
        return item


class DBPipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client.youla_images

    def process_item(self, item, spider):
        self.db[spider.collection].update_one({'_id': item['_id']},
                                              {'$set': item},
                                              upsert=True)
        logger.debug('Vacancy added to MongoDB')
        return item
