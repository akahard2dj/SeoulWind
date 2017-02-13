from Crawler.Pref import url_info
from Crawler.Utils.parameters import Parameters
import requests
import json


class GGAirCrawler:
    def __init__(self, parameter_file):
        self.__pminfo = list()
        self.__params = Parameters(parameter_file).load()

    def parser(self):
        res = requests.get(url_info.get_gg_air_pminfo())
        res_json = json.loads(res.text)
        n_obs = len(res_json['all_site_data'])
        for idx in range(n_obs):
            '''
            datao3total 0.038
            citydong 가평
            datacototal 0.4
            wspeed 3.5
            datapm25total 미설치
            datano2total 0.014
            wdata 북동
            datapm10total 54
            wfire 9.6
            cityname 가평군
            dataso2total 0.004
            sitecode 131611
            '''
            print(res_json['all_site_data'][idx]['citydong'])
