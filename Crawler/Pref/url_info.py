
def get_seoul_openapi_windinfo(apikey):
    #http://openapi.seoul.go.kr:8088/4f5972564c616b6134344843436f4b/json/RealtimeWeatherStation/1/30/
    url = 'http://openapi.seoul.go.kr:8088/{}/json/RealtimeWeatherStation/1/26/'.format(apikey)
    return url


def get_seoul_openapi_pminfo(apikey):
    url = 'http://openapi.seoul.go.kr:8088/{}/json/RealtimeCityAir/1/25/'.format(apikey)
    return url


def get_gg_air_pminfo():
    url = 'http://air.gg.go.kr/airgg/include/php/json/json_pf.php'
    return url
