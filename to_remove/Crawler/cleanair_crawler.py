from bs4 import BeautifulSoup
import requests

col_name_table = ['ObservatoryLocation', 'PM_10', 'PM_2.5', 'O3', 'NO2', 'CO', 'SO2',
                  'AirIndex_Grade', 'AirIndex', 'AirIndex_Key']

url = 'http://cleanair.seoul.go.kr/air_city.htm?method=measure'
res = requests.get(url)


soup = BeautifulSoup(res.text, "html.parser")
table_pages = soup.find('table', {'class': 'tbl2'})
air_items = table_pages.find('tbody').findAll('tr')
for idx, air in enumerate(air_items[1:]):
    item_dict = dict()
    td_item = air.findAll('td')
    item_values = list()
    for td in td_item:
        item_values.append(td.text.strip())

    for sub_idx, item in enumerate(item_values[0:len(col_name_table)]):
        item_dict[col_name_table[sub_idx]] = item

    print(item_dict)