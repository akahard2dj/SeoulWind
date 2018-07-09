import itertools
import json

from django.http import HttpRequest
from django.http import HttpResponse, JsonResponse
from django.template import loader

from crawlers.models import AirPollution, WeatherData


def get_json():
    a_last = AirPollution.objects.last()
    w_last = WeatherData.objects.last()

    a_set = AirPollution.objects.filter(timestamp=a_last.timestamp).all()
    w_set = WeatherData.objects.filter(timestamp=w_last.timestamp).all()

    a_var = list(a_set[0].__dict__.keys())
    w_var = list(w_set[0].__dict__.keys())
    a_var.remove('_state')
    a_var.remove('id')
    w_var.remove('_state')
    w_var.remove('id')
    w_var.remove('timestamp')
    w_var.remove('observatory_id')
    w_var.remove('wind_direction_value')
    w_var.remove('wind_direction_str')
    w_var.remove('wind_speed')
    merged_var = list(itertools.chain(a_var, w_var))
    merged_var.append('observatory_name')
    merged_var.append('coordinates')
    merged_var.append('wind')

    SeoulWindData = type("SeoulWindData", (), {k: 0 for k in merged_var})

    s_data_list = list()
    for w in w_set:
        for a in a_set:
            if a.observatory == w.observatory:
                s_data = SeoulWindData()
                # s_data.timestamp = w.timestamp
                s_data.observatory_id = w.observatory.id
                s_data.observatory_name = w.observatory.name
                # s_data.wind_direction_value = w.wind_direction_value
                # s_data.wind_direction_str = w.wind_direction_str
                # s_data.wind_speed = w.wind_speed
                s_data.temperature = w.temperature
                s_data.precipitation = w.precipitation
                s_data.humidity = w.humidity
                s_data.timestamp = a.timestamp
                if a.pm10 == -999:
                    break
                else:
                    s_data.pm10 = a.pm10

                s_data.pm25 = a.pm25
                s_data.o3 = a.o3
                s_data.no2 = a.no2
                s_data.co = a.co
                s_data.so2 = a.so2
                s_data.coordinates = [w.observatory.lng, w.observatory.lat]
                s_data.wind = [w.wind_direction_value, w.wind_speed]
                s_data_list.append(s_data)
                break

    arr = []
    for s_data in s_data_list:
        d = {}
        for column in SeoulWindData.__dict__:
            if column in merged_var:
                d[column] = getattr(s_data, column)

        arr.append(d)

    return json.dumps(arr)


def index(request: HttpRequest):
    template = loader.get_template('windows/index.html')
    ctx = {"data_type": "pm25"}

    return HttpResponse(template.render(ctx))


def redirect_page(request: HttpRequest, data_type):
    json_url = '/data/current/'
    template = loader.get_template('windows/index.html')
    ctx = {"data_type": data_type, "data_sample": json_url}

    return HttpResponse(template.render(ctx))


def get_data(request: HttpRequest):
    result = get_json()
    return HttpResponse(result, content_type='application/json')
