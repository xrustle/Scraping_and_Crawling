from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import re
from pymongo import MongoClient

REQUEST = 'data scientist'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                         'AppleWebKit/537.36 (KHTML, like Gecko)' 
                         'Chrome/79.0.3945.79 Safari/537.36'}


def parse_salary(salary):
    sal_from = None
    sal_to = None
    currency = None
    if salary:
        salary = re.sub(r'\s+', '', salary.text)
        if not salary.find('от'):
            re_search = re.search(r'(\d+)(.+)', salary)
            if re_search:
                sal_from = int(re_search.group(1))
                currency = re_search.group(2)
        elif not salary.find('до'):
            re_search = re.search(r'(\d+)(.+)', salary)
            if re_search:
                sal_to = int(re_search.group(1))
                currency = re_search.group(2)
        else:
            re_search = re.search(r'(\d+)-(\d+)(.+)', salary)
            if re_search:
                sal_from = int(re_search.group(1))
                sal_to = int(re_search.group(2))
                currency = re_search.group(3)
    return sal_from, sal_to, currency


def parse_hh_page(page_num):
    link = hh_link + '&page=' + str(page_num) if page_num else hh_link

    html = requests.get(link, headers=HEADERS).text
    parsed_html = bs(html, 'lxml')

    vacancy_list = parsed_html.findAll('div', {'data-qa': 'vacancy-serp__vacancy'})

    for vacancy in vacancy_list:
        vac_dict = {}
        title = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
        vac_dict['title'] = title.text

        salary = vacancy.find('div', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        vac_dict['min_salary'], vac_dict['max_salary'], vac_dict['currency'] = parse_salary(salary)

        re_search = re.search(r'(.+)\?', title['href'])
        vac_dict['_id'] = re_search.group(1)
        vac_dict['source'] = 'hh.ru'

        location = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-address'})
        vac_dict['location'] = location.text if location else None

        company = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'})
        vac_dict['company'] = company.text if company else None

        data.append(vac_dict)

    return parsed_html


def parse_sj_page(page_num):
    link = main_link + '&page=' + str(page_num) if page_num else main_link

    html = requests.get(link, headers=HEADERS).text
    parsed_html = bs(html, 'lxml')

    vacancy_list = parsed_html.findAll('div', {'class': 'f-test-vacancy-item'})

    for vacancy in vacancy_list:
        vac_dict = {}
        title = vacancy.find('a', {'class': '_1QIBo'})
        vac_dict['title'] = title.text
        salary = vacancy.find('span', {'class': '_2VHxz'})
        vac_dict['min_salary'], vac_dict['max_salary'], vac_dict['currency'] = parse_salary(salary)
        re_search = re.search(r'(.+)\?', super_link + title['href'])
        if re_search:
            vac_dict['_id'] = re_search.group(1)
        else:
            vac_dict['_id'] = super_link + title['href']
        vac_dict['source'] = 'superjob.ru'

        loc_block = vacancy.find('span', {'class': '_3Ll36'})
        if loc_block:
            loc = loc_block.find_next_sibling()
            vac_dict['location'] = loc.text if loc else None
        else:
            vac_dict['location'] = None

        vac_dict['company'] = vacancy.find('a', {'class': '_205Zx'}).text

        data.append(vac_dict)
    return parsed_html


data = []

hh_link = 'https://hh.ru/search/vacancy?'\
          'area=1&'\
          'L_is_autosearch=false&'\
          'clusters=true&'\
          'enable_snippets=true'\
          '&text={}'.format(REQUEST.replace(' ', '+'))

first_page_html = parse_hh_page(0)

page_numbers = first_page_html.find_all('a', {'data-page': True})
max_page = max([int(page['data-page']) for page in page_numbers]) if page_numbers else 0

for i in range(1, max_page + 1):
    parse_hh_page(i)

super_link = 'https://www.superjob.ru'
main_link = super_link + '/vacancy/search/?keywords={}&geo%5Bt%5D%5B0%5D=4'.format(REQUEST.replace(' ', '%20'))

first_page_html = parse_sj_page(None)

page_numbers = first_page_html.find_all('span', {'class': '_2GT-y'})
max_page = max([int(page.text) for page in page_numbers if page.text.isdigit()]) if page_numbers else 0

for i in range(1, max_page + 1):
    parse_sj_page(i)


client = MongoClient('localhost', 27017)
db = client['db']
vacancies = db.vacancies


# Функция записи и обновления данных о вакансиях в коллекцию MongoDB
# Используется функция update_one с параметром upsert=True. Если запись не найдена, то она будет добавлена.
# В качестве ключа используются прямые ссылки на вакансии
def db_insert():
    for vacancy in data:
        vacancies.update_one({'_id': vacancy['_id']},
                             {'$set': vacancy},
                             upsert=True)


# Функция выводит вакансии с зарплатой больше параметра min_salary
def db_show(min_salary):
    objects = vacancies.find({'$or': [{'min_salary': {'$gt': min_salary}},
                                      {'max_salary': {'$gt': min_salary}}]})
    for obj in objects:
        pprint(obj)


db_insert()
db_show(100000)
