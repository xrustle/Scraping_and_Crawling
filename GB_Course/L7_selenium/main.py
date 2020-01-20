from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import time

driver = webdriver.Chrome()
driver.get('https://geekbrains.ru/login')

assert 'GeekBrains' in driver.title
elem = driver.find_element_by_id('user_email')
elem.send_keys('study.ai_172@mail.ru')
elem = driver.find_element_by_id('user_password')
elem.send_keys('Password172')

elem.send_keys(Keys.RETURN)
assert 'Главная' in driver.title

profile = driver.find_element_by_class_name('avatar')
driver.get(profile.get_attribute('href'))

edit_profile = driver.find_element_by_class_name('text-sm')
driver.get(edit_profile.get_attribute('href'))

'''Первый способ выбора из списка'''
gender = driver.find_element_by_name('user[gender]')
# options = gender.find_elements_by_tag_name('option')
#
# for option in options:
#     if option.text == 'Женский':
#         option.click()
'''Второй способ выбора из списка'''
select = Select(driver.find_element_by_name('user[gender]'))
select.select_by_value('2')

gender.submit()  # Подтверждение

# Методы перехода по истории
# driver.back()
# driver.back()
# time.sleep(3)
# driver.forward()


# driver.quit()
