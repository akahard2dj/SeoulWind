from parameters import Parameters

from bs4 import BeautifulSoup
import requests
import json


def addr2latlng(addr):
    params = Parameters('parameters.txt').load()
    payload = {'clientID': params['apikey_naver_id'], 'query': addr}
    headers = {
                'Host': 'openapi.naver.com',
                'User-Agent': 'curl/7.43.0',
                'Accept': '*/*',
                'Content-Type': 'application/json',
                'X-Naver-Client-Id': params['apikey_naver_id'],
                'X-Naver-Client-Secret': params['apikey_naver_secret'],
            }

    url = 'https://openapi.naver.com/v1/map/geocode?clientId={}&query={}'.format(params['apikey_naver_id'], addr)
    res = requests.get(url, data=json.dumps(payload), headers=headers)
    output = json.loads(res.text)

    try:
        x = output['result']['items'][0]['point']['x']
        y = output['result']['items'][0]['point']['y']
    except KeyError:
        x = 0.0
        y = 0.0

    return x, y

f = open('observatory.csv', 'w', encoding='utf8')

url = 'http://cleanair.seoul.go.kr/inform.htm?method=observatory'
res = requests.get(url)

soup = BeautifulSoup(res.text, "html.parser")
table_pages = soup.find('table', {'class': 'tbl4'})
loc_items = table_pages.find('tbody').findAll('tr')
for loc in loc_items:
    td_item = loc.findAll('td')
    item_dict = dict()
    addr_str = td_item[1].text.strip().split(' ')
    item_dict['ObservatoryLocation'] = addr_str[1]
    str_index = addr_str[3].find('(')
    addr_str[3] = addr_str[3][0:str_index]
    addr = ' '.join(addr_str[0:4])
    latlng = addr2latlng(addr)
    msg = '{},{},{},{},\n'.format(addr_str[1], str(latlng[1]), str(latlng[0]), addr)
    # exception
    # 마포구,37.5734407,126.90072,서울시 마포구 성중길 82,
    f.write(msg)

f.close()