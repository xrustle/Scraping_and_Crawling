import requests
from lxml import html
from pymongo import MongoClient
from hashlib import sha1
from datetime import datetime, timedelta
from pprint import pprint
import re

client = MongoClient('localhost', 27017)
db = client['news']


def db_insert_many(data):
    for news in data:
        db.news.update_one({'_id': news['_id']},
                           {'$set': news},
                           upsert=True)


def db_show():
    objects = db.news.find()
    for obj in objects:
        pprint(obj)


def get_root(url):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                                                        'Chrome/79.0.3945.88 Safari/537.36'})
    return html.fromstring(response.text)


def get_mail_data():
    main_link = 'https://mail.ru'
    root = get_root(main_link)
    news_items = root.xpath("//div[contains(@class, 'news')]/div[contains(@class, 'news-item')]//a[last()]")
    news_list = []

    if news_items:
        for news_item in news_items:
            news = {}
            link = news_item.xpath("./@href")
            if link:
                link = link[0].split('?', maxsplit=1)[0]
                news_item_root = get_root(link)
                title = news_item.xpath("./text()")
                date_n_time = news_item_root.xpath("//span[@datetime]/@datetime")
                source = news_item_root.xpath("//span[@class='breadcrumbs__item'][last()]"
                                              "//span[@class='link__text']/text()")

                news['link'] = link
                news['_id'] = sha1(link.encode('utf-8')).hexdigest()
                if title:
                    news['title'] = title[0].replace(u'\xa0', u' ')
                if source:
                    news['source'] = source[0]
                if date_n_time:
                    news['date'] = datetime.strptime(date_n_time[0], '%Y-%m-%dT%H:%M:%S%z')
                news_list.append(news)
    return news_list


def get_yandex_data():
    main_link = 'https://yandex.ru'
    root = get_root(main_link + '/news')
    news_items = root.xpath("//div[@class='stories-set__main-item'] | //td[@class='stories-set__item']")
    news_list = []

    if news_items:
        for news_item in news_items:
            news = {}
            link = news_item.xpath(".//div[@class='story__topic']/h2/a/@href")
            if link:
                link = main_link + link[0].split('?', maxsplit=1)[0]
                title = news_item.xpath(".//div[@class='story__topic']/h2/a/text()")
                source_n_date = news_item.xpath(".//div[@class='story__date']/text()")

                news['link'] = link
                news['_id'] = sha1(link.encode('utf-8')).hexdigest()
                if title:
                    news['title'] = title[0]
                if source_n_date:
                    re_search = re.search(r'(.*) (.*)', source_n_date[0])
                    if re_search:
                        news['source'] = re_search[1]
                        news['date'] = datetime.today().replace(hour=0,
                                                                minute=0,
                                                                second=0,
                                                                microsecond=0).astimezone()
                        time_re_search = re.search(r'(\d{2}):(\d{2})', re_search[2])
                        if time_re_search:
                            news['date'] = news['date'].replace(hour=int(time_re_search[1]),
                                                                minute=int(time_re_search[2]))
                        if len(re_search[2]) > 5:
                            news['date'] -= timedelta(days=1)
                news_list.append(news)
    return news_list


def get_lenta_data():  # Беру только новости. Игнорирую топики, ссылки на новости сторонних ресурсов, истории и т.д.
    main_link = 'https://lenta.ru/'
    root = get_root(main_link)
    news_items = root.xpath("//div[contains(@class, 'item') and not(contains(@class, 'news'))]"
                            "/a[starts-with(@href, '/news/')]")
    news_list = []

    if news_items:
        for news_item in news_items:
            news = {}
            link = news_item.xpath("./@href")
            if link:
                link = main_link + link[0].split('?', maxsplit=1)[0]
                news_item_root = get_root(link)
                title = news_item_root.xpath("//div[@class='b-topic__content']//h1[@class='b-topic__title']/text()")
                date_n_time = news_item_root.xpath("//div[@class='b-topic__content']//time/@datetime")

                news['link'] = link
                news['_id'] = sha1(link.encode('utf-8')).hexdigest()
                news['source'] = 'lenta.ru'
                if title:
                    news['title'] = title[0].replace(u'\xa0', u' ')
                if date_n_time:
                    news['date'] = datetime.strptime(date_n_time[0], '%Y-%m-%dT%H:%M:%S%z')
                news_list.append(news)
    return news_list


if __name__ == '__main__':
    funcs = [get_yandex_data,
             get_mail_data,
             get_lenta_data]

    for get_data in funcs:
        db_insert_many(get_data())

    db_show()
