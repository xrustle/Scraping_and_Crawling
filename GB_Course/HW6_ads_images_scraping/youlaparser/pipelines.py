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


class ScriptParsingPipeline(object):
    def process_item(self, item, spider):
        rec = {'url': item['url']}
        re_search = re.search(r'{.*}', item['data'])
        if re_search:
            item['data'] = json.loads(re_search.group(0))
            entities = item['data'].get('entities')
            if entities:
                cities = entities.get('cities')
                products = entities.get('products')
                if products:
                    # pprint(products[0])
                    rec['title'] = products[0].get('name')
                    rec['description'] = products[0].get('description')
                    images = products[0].get('images')
                    if images:
                        rec['images'] = [image['url'] for image in images]
                    location = products[0].get('location')
                    if location:
                        rec['location'] = location['description']
                    rec['price'] = products[0].get('price')
                    if rec['price']:
                        rec['price'] = rec['price'] / 100
                    attributes = products[0].get('attributes')
                    if attributes:
                        rec['attributes'] = {}
                        for attr in attributes:
                            key = attr['slug']
                            value = attr['values'][0]['value']
                            if key == 'price' and int(value):
                                value = int(value) / 100
                            rec['attributes'][key] = value
        item = rec
        return item


class YoulaImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        images = item.get('images')
        if images:
            for image in images:
                try:
                    yield scrapy.Request(image)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['images'] = [itm[1] for itm in results if itm[0]]
        return item


class DBPipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        client.drop_database('youla_images')
        self.mongo_base = client.youla_images

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item
