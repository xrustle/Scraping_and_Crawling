from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from pymongo import MongoClient
from hashlib import sha1
from datetime import datetime, timedelta
import time
import re

URL = 'https://account.mail.ru/login'
CREDENTIALS = {
    'Login': 'study.ai_172',
    'Password': 'NewPassword172'
}
MONTHES = ['января', 'февраля', 'марта',
           'апреля', 'мая', 'июня',
           'июля', 'августа', 'сентября',
           'октября', 'ноября', 'декабря']

def parse_date(date):
    if date.startswith('Сегодня') or date.startswith('Вчера'):
        if date.startswith('Сегодня'):
            pattern = 'Сегодня'
            d = datetime.now()
        else:
            pattern = 'Вчера'
            d = datetime.now() - timedelta(1)
        day = d.day
        month = MONTHES[d.month - 1]
        return date.replace(pattern, f'{d.day} {month}')
    return date

def parse_sender(sender):
    re_search = re.search(r'<(.+)>$', sender)
    return re_search.group(1)


'''Класс Mongo'''
class DB:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client.mailru

    def insert_data(self, email):
        content = email.find_element_by_class_name('llc__content')
        item = {
            'sender': content.find_element_by_class_name('ll-crpt').get_attribute('title'),
            'title': content.find_element_by_class_name('ll-sj__normal').text,
            'snippet': content.find_element_by_class_name('ll-sp__normal').text,
            'date': content.find_element_by_class_name('llc__item_date').get_attribute('title')
        }
        item['sender'] = parse_sender(item['sender'])
        item['date'] = parse_date(item['date'])
        item['_id'] = sha1((str(item['date']) + item['sender'] + item['title']).encode('utf-8')).hexdigest()
        self.db['emails'].update_one({'_id': item['_id']},
                                     {'$set': item},
                                     upsert=True)


def add_new_email_urls(add_all=False):
    if add_all:
        for email in emails:
            href = email.get_attribute('href')
            email_urls.append(href)
            db.insert_data(email)
        print(f'Добавлено писем: {len(emails)}')
    else:
        last_added_email_num = len(emails) - 1
        current_url = emails[last_added_email_num].get_attribute('href')
        while current_url != prev_btm_url:
            last_added_email_num -= 1
            current_url = emails[last_added_email_num].get_attribute('href')
        for i in range(last_added_email_num + 1, len(emails)):
            href = emails[i].get_attribute('href')
            email_urls.append(href)
            db.insert_data(emails[i])
        print(f'Добавлено писем: {len(emails) - last_added_email_num - 1}')

if __name__ == '__main__':
    driver = webdriver.Chrome()
    print('Заходим на страницу ввода логина/пароля')
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(URL)

    '''Вводим логин и пароль'''
    for cred in CREDENTIALS:
        element = Wait(driver, 10).until(
            EC.visibility_of_element_located((
                By.NAME, cred
            ))
        )
        print(f'{cred} entering...')
        element.send_keys(CREDENTIALS[cred])
        element.send_keys(Keys.RETURN)

    '''В этом списке будем хранить ссылки на письма'''
    email_urls = []

    print('Ждем появления строк с письмами...')
    emails = Wait(driver, 10).until(
        EC.visibility_of_all_elements_located((
            By.CLASS_NAME, 'js-letter-list-item'
        ))
    )
    new_btm_url = emails[-1].get_attribute('href')

    db = DB()

    print('Начинаем добавлять письма...')
    add_new_email_urls(add_all=True)
    for i in range(3):
        ActionChains(driver).move_to_element(emails[-1]).perform()
        emails = Wait(driver, 10).until(
            EC.visibility_of_all_elements_located((
                By.CLASS_NAME, 'js-letter-list-item'
            ))
        )
    prev_btm_url = new_btm_url
    new_btm_url = emails[-1].get_attribute('href')

    '''Скроллим пока самое нижнее письмо после прокрутки не совпадет с самым нижним письмом до прокрутки.
    Это будет означать, что мы прокрутили до конца.'''
    while new_btm_url != prev_btm_url:
        '''Скроллим с помощью перемещения к последнему письму на текущий момент, 
        чтобы появились новые'''
        add_new_email_urls()
        for i in range(3):
            ActionChains(driver).move_to_element(emails[-1]).perform()
            emails = Wait(driver, 10).until(
                EC.visibility_of_all_elements_located((
                    By.CLASS_NAME, 'js-letter-list-item'
                ))
            )
        prev_btm_url = new_btm_url
        new_btm_url = emails[-1].get_attribute('href')

    '''Теперь у нас есть все ссылки на письма. 
    Можно также пройтись и собрать подробную информацию, заходя в каждое письмо.'''
    print(f'Всего писем добавлено: {len(email_urls)}')
    print('Конец')
    driver.quit()
