from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

options = Options()
'''Во весь экран'''
# options.add_argument('start-maximized')
'''Не открывая окно'''
options.add_argument('--headless')

driver = webdriver.Chrome(options=options)
driver.get('https://5ka.ru/special_offers')
print('Открыта главная страница')
clicks = 0
while True:
    try:
        more_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.CLASS_NAME, 'special-offers__more-btn'
            ))
        )
        # more_btn = driver.find_element_by_class_name('special-offers__more-btn')
        more_btn.click()
        clicks += 1
        print(f'Обработано страниц {clicks}')
    except Exception as e:
        print(e)
        print(f'Нажатий {clicks}')
        break

goods = driver.find_elements_by_class_name('sale-card')
for good in goods:
    try:
        print(good.find_element_by_class_name('sale-card__title').text)
        print(float(good
                    .find_element_by_class_name('sale-card__price--new')
                    .find_element_by_xpath('span[1]')
                    .text)/100)
    except:
        print('Конец')
