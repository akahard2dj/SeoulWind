from django.http import HttpRequest, JsonResponse

import requests
from bs4 import BeautifulSoup
from crawlers.models import WeatherData, Observatory, AirPollution


def _weather_info():
    url = 'http://aws.seoul.go.kr/RealTime/RealTimeWeatherUser.asp?TITLE=%C0%FC%20%C1%F6%C1%A1%20%C7%F6%C8%B2'
    res = requests.get(url)
    res.encoding = 'EUC-KR'

    soup = BeautifulSoup(res.text, "html.parser")
    current_time_html = soup.find('td', {'class': 'explain'}).text.rstrip().strip()
    tmp = current_time_html.split(' ')

    current_time_str = ''
    for time_item in tmp[:-1]:
        current_time_str += str(time_item[:-1])

    current_time_str += '00'
    #print(current_time_str)
    data_boxes = soup.find_all('td', {'valign': 'top'})
    aws_seoul_items = data_boxes[0].find_all('tr', {'valign': 'top'})
    for aws_seoul in aws_seoul_items[1:]:
        spot_data = aws_seoul.find_all('td')

        name = spot_data[1].text.strip()[4:]
        wind_dir_value = spot_data[2].text.strip() if spot_data[2].text.strip() != '-' else -999.0
        wind_dir_str = spot_data[3].text.strip()
        wind_speed = spot_data[4].text.strip() if spot_data[4].text.strip() != '-' else -999.0
        temp = spot_data[5].text.strip() if spot_data[5].text.strip() != '-' else -999.0
        preci = spot_data[6].text.strip() if spot_data[6].text.strip() != '-' else -999.0
        rain = spot_data[7].text.strip() if spot_data[7].text.strip() != '-' else -999.0
        hum = spot_data[8].text.strip() if spot_data[8].text.strip() != '-' else -999.0
        sol_rad = spot_data[9].text.strip()
        sunshine = spot_data[10].text.strip()
        # print(name, wind_dir_str, wind_speed, temp, preci, rain, hum, sol_rad, sunshine)

        observatory = Observatory.objects.filter(aws_type_name='서울시청AWS').get(name=name)

        wea_data = WeatherData()
        wea_data.timestamp = current_time_str
        wea_data.wind_direction_value = wind_dir_value
        wea_data.wind_direction_str = wind_dir_str
        wea_data.wind_speed = wind_speed
        wea_data.temperature = temp
        wea_data.precipitation = preci
        wea_data.humidity = hum
        wea_data.observatory = observatory

        check_query = WeatherData.objects.last()
        if check_query.timestamp == wea_data.timestamp:
            break
        else:
            wea_data.save()


def _air_pollution_info():
    url = 'http://cleanair.seoul.go.kr/air_city.htm?method=measure&grp1=pm10'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    table_data_html = soup.find('table', {'class': 'tbl2'})
    obs_data_html = table_data_html.find('tbody').find_all('tr')

    for items in obs_data_html[1:]:
        time_str = items.find('th').text.rstrip().strip()
        time_tmp = time_str.split(' ')
        time = ''.join(time_tmp[0].split('-')) + ''.join(time_tmp[1].split(':'))
        tmp = items.find_all('td')
        name = tmp[0].text.rstrip().strip()[:-1] \
            if len(tmp[0].text.rstrip().strip()) != 2 else tmp[0].text.rstrip().strip()
        pm10 = tmp[1].text.rstrip().strip() if tmp[1].text.rstrip().strip() != '점검중' else -999
        pm25 = tmp[2].text.rstrip().strip() if tmp[2].text.rstrip().strip() != '점검중' else -999
        o3 = tmp[3].text.rstrip().strip() if tmp[3].text.rstrip().strip() != '점검중' else -999
        no2 = tmp[4].text.rstrip().strip() if tmp[4].text.rstrip().strip() != '점검중' else -999
        co = tmp[5].text.rstrip().strip() if tmp[5].text.rstrip().strip() != '점검중' else -999
        so2 = tmp[6].text.rstrip().strip() if tmp[6].text.rstrip().strip() != '점검중' else -999

        observatory = Observatory.objects.filter(aws_type_name='서울시청AWS').get(name=name)
        airpoll = AirPollution()
        airpoll.observatory = observatory
        airpoll.timestamp = time
        airpoll.pm10 = pm10
        airpoll.pm25 = pm25
        airpoll.o3 = o3
        airpoll.no2 = no2
        airpoll.co = co
        airpoll.so2 = so2

        check_query = AirPollution.objects.last()
        if check_query.timestamp == airpoll.timestamp:
            break
        else:
            airpoll.save()


def update_data(request: HttpRequest):
    _weather_info()
    _air_pollution_info()

    return JsonResponse({'msg': 'updated'})
