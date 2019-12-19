from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
html = requests.get('http://127.0.0.1:5000/').text
# parsed_html = bs(html, 'html.parser')
parsed_html = bs(html, 'lxml')

links = parsed_html.find_all('a')
div_link = parsed_html.find('a').find_parent()
head_div = div_link.find_parent()
children = head_div.findChildren(recursive=False)

parents = children[1].findParents()
text = children[1].findChild().getText()

link_href = children[1].findChild()['href']

elem = parsed_html.find(attrs={'href': '#'})
elem2 = parsed_html.find_all('p', {'class': 'red'})
elem3 = parsed_html.find_all('p', limit=3)
elem4 = parsed_html.find_all(text='РЁРµСЃС‚РѕР№ РїР°СЂР°РіСЂР°С„')[0].findParent()

pprint(elem)
