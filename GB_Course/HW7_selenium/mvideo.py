from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
from hashlib import sha1
import time

URL = 'https://www.mvideo.ru/'

'''Получение числа из текста внутри элемента внутри parent c переданным css классом'''
def get_number(parent, css_class):
    try:
        text = parent.find_element_by_class_name(css_class).text
        if not text or text == '':
            return None
    except:
        return None
    return int(''.join(filter(lambda x: x.isdigit(), text)))


'''Класс Mongo'''
class DB:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client.mvideo

    def insert_data(self, parent):
        goods = parent.find_elements_by_class_name('gallery-list-item')
        for good in goods:
            title = good.find_element_by_class_name('sel-product-tile-title').text
            if title:
                item = {
                    '_id': sha1(title.encode('utf-8')).hexdigest(),
                    'title': title,
                    'price': get_number(good, 'c-pdp-price__current')  # Текущая цена
                }
                for attr in [
                    'discount',  # Скидка
                    'trade-price',  # Цена по трейд-ин
                    'monthly'  # Цена в рассрочку за месяц
                ]:
                    value = get_number(good, f'c-pdp-price__{attr}')
                    if value:
                        item[attr] = value

                self.db['hits'].update_one({'_id': item['_id']},
                                           {'$set': item},
                                           upsert=True)
                print('Товар добавлен в базу')


if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(URL)
    print('Зашли на главную страницу mvideo')

    '''XPath целиком для карусели хитов прожаж и отдельно для кнопки пролистывания Далее'''
    carousel_xpath = '//div[contains(text(), "Хиты продаж")]/../../..'
    next_btn_xpath = carousel_xpath + '//a[contains(@class, "next-btn")]'

    '''Находим карусель с хитами и переходимна нее'''
    carousel = driver.find_element_by_xpath(carousel_xpath)
    ActionChains(driver).move_to_element(carousel).perform()
    print('Перешли к карусели с хитами продаж')

    next_btn = carousel.find_element_by_xpath(next_btn_xpath)

    db = DB()
    db.insert_data(carousel)
    while next_btn.is_displayed():
        next_btn.click()
        print('Перешли на следующую страницу')
        time.sleep(1)  # Дожидаемся завершения анимации кручения карусели
        db.insert_data(carousel)

    driver.quit()
