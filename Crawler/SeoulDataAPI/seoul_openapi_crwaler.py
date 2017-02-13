from Crawler.Pref import url_info
from Crawler.Pref import ref
from Crawler.Utils.parameters import Parameters

import requests
import json
import os


class Info2JsonSeoul:
    def __init__(self, parameter_filename):
        self.__pminfo = list()
        self.__windinfo = list()
        self.__params = Parameters(parameter_filename).load()

    def gather_data(self):
        pminfo = PMInfoCrawler(self.__params).get_result()
        windinfo = WindInfoCrawler(self.__params).get_result()
        pminfo_name = list()
        windinfo_name = list()
        if isinstance(pminfo, dict):
            for idx in range(pminfo['RealtimeCityAir']['list_total_count']):
                raw_name = pminfo['RealtimeCityAir']['row'][idx]['MSRSTE_NM']
                if len(raw_name) > 2:
                    name = raw_name[0:-1]
                else:
                    name = raw_name
                pminfo_name.append(name)

        if isinstance(windinfo, dict):
            for idx in range(windinfo['RealtimeWeatherStation']['list_total_count']):
                windinfo_name.append(windinfo['RealtimeWeatherStation']['row'][idx]['STN_NM'])

        #print(pminfo)
        #print(windinfo)
        f = open(os.path.join('Crawler', 'data', 'observatory.csv'), 'r', encoding='utf8')
        obs = f.readlines()
        f.close()
        obs_name = list()
        for line in obs[1:]:
            obs_name.append(line.split(',')[0])

        out_json = list()
        if isinstance(pminfo, dict):
            for idx in range(pminfo['RealtimeCityAir']['list_total_count']):
                item = dict()
                item['name'] = pminfo_name[idx]
                idx_station = obs_name.index(item['name'])
                idx_wind = windinfo_name.index(item['name'])

                lat = obs[idx_station+1].split(',')[2]
                lng = obs[idx_station+1].split(',')[1]
                item['coordinates'] = [lat, lng]
                wind_dir = (int(windinfo['RealtimeWeatherStation']['row'][idx_wind]['CODE'])-1) * 22.5
                wind_speed = windinfo['RealtimeWeatherStation']['row'][idx_wind]['SAWS_WS_AVG']
                item['wind'] = [wind_dir, wind_speed]
                item['temp'] = windinfo['RealtimeWeatherStation']['row'][idx_wind]['SAWS_TA_AVG']
                item['hum'] = windinfo['RealtimeWeatherStation']['row'][idx_wind]['SAWS_HD']
                item['in'] = windinfo['RealtimeWeatherStation']['row'][idx_wind]['SAWS_SOLAR']
                item['o3'] = pminfo['RealtimeCityAir']['row'][idx]['O3']
                item['co'] = pminfo['RealtimeCityAir']['row'][idx]['CO']
                item['so2'] = pminfo['RealtimeCityAir']['row'][idx]['SO2']
                item['no2'] = pminfo['RealtimeCityAir']['row'][idx]['NO2']
                item['pm10'] = pminfo['RealtimeCityAir']['row'][idx]['PM10']
                item['pm25'] = pminfo['RealtimeCityAir']['row'][idx]['PM25']
                item['timestamp'] = windinfo['RealtimeWeatherStation']['row'][idx]['SAWS_OBS_TM']
                out_json.append(item)

        #with open(os.path.join('web', 'static', 'data', 'obs-2.json'), 'w', encoding='utf8') as outfile:
        #    json.dump(out_json, outfile)

        return out_json


class PMInfoCrawler:
    def __init__(self, params):
        self.__data = list()
        self.__json = list()
        self.__date = None
        self.__params = params
        self.parser()

    def write_json(self):
        if self.__data:
            print('writing...')
            out_json = dict()
            out_json['DATE'] = self.__date
            out_json['DATA'] = self.__data
            with open(os.path.join('static','pminfo.json'), 'w', encoding='utf8') as outfile:
                json.dump(out_json, outfile)

    def get_result(self):
        return self.__json

    def parser(self):
        url = url_info.get_seoul_openapi_pminfo(self.__params['apikey_seoul'])
        res = requests.get(url)
        res_json = json.loads(res.text)
        self.__json = res_json
        '''
        result_code = res_json['RealtimeCityAir']['RESULT']['CODE']
        if result_code == ref.SEOUL_OPENAPI_OK_STATUS:
            f = open(os.path.join('static', 'observatory.csv'), 'r', encoding='utf8')
            obs = f.readlines()
            f.close()
            obs_name = list()
            for line in obs[1:]:
                obs_name.append(line.split(',')[0])

            num_observatory = res_json['RealtimeCityAir']['list_total_count']
            for idx in range(num_observatory):
                item = dict()
                item['STATION_NAME'] = res_json['RealtimeCityAir']['row'][idx]['MSRSTE_NM']
                if len(item['STATION_NAME']) > 2:
                    name = item['STATION_NAME'][0:-1]
                else:
                    name = item['STATION_NAME']
                find_idx = obs_name.index(name)
                item['lng'] = float(obs[find_idx + 1].split(',')[1])
                item['lat'] = float(obs[find_idx + 1].split(',')[2])
                item['PM10'] = res_json['RealtimeCityAir']['row'][idx]['PM10']
                item['PM25'] = res_json['RealtimeCityAir']['row'][idx]['PM25']
                item['O3'] = res_json['RealtimeCityAir']['row'][idx]['O3']
                item['NO2'] = res_json['RealtimeCityAir']['row'][idx]['NO2']
                item['CO'] = res_json['RealtimeCityAir']['row'][idx]['CO']
                item['SO2'] = res_json['RealtimeCityAir']['row'][idx]['SO2']
                self.__date = res_json['RealtimeCityAir']['row'][idx]['MSRDT']
                self.__data.append(item)
            else:
                print('Parsing Error: {}'.format(result_code))
        '''


class WindInfoCrawler:
    def __init__(self, params):
        self.__data = list()
        self.__json = list()
        self.__params = params
        self.parser()

    def write_csv(self):
        if self.__data:
            print('writing...')
            with open(os.path.join('static', 'windinfo.csv'), 'w', encoding='utf8') as outfile:
                json.dump(self.__data, outfile)

            f = open(os.path.join('static', 'data_wind.csv'), 'w', encoding='utf8')
            msg = 'lat,lng,angle,windspeed\n'
            f.write(msg)
            for idx, item in enumerate(self.__data):
                msg='{},{},{},{}\n'.format(item['lat'], item['lon'],(item['WIND_CODE']-1)*15.0, item['WIND_SPEED_AVG'])
                f.write(msg)
            f.close()

    def get_result(self):
        return self.__json

    def parser(self):
        url = url_info.get_seoul_openapi_windinfo(self.__params['apikey_seoul'])
        res = requests.get(url)
        res_json = json.loads(res.text)
        self.__json = res_json
        result_code = res_json['RealtimeWeatherStation']['RESULT']['CODE']
        '''
        if result_code == ref.SEOUL_OPENAPI_OK_STATUS:
            f = open(os.path.join('static', 'observatory.csv'), 'r', encoding='utf8')
            obs = f.readlines()
            f.close()
            obs_name = list()
            for line in obs[1:]:
                obs_name.append(line.split(',')[0])

            num_observatory = res_json['RealtimeWeatherStation']['list_total_count']
            for idx in range(num_observatory):
                item = dict()
                item['STATION_NAME'] = res_json['RealtimeWeatherStation']['row'][idx]['STN_NM']
                find_idx = obs_name.index(item['STATION_NAME'])

                item['TA'] = res_json['RealtimeWeatherStation']['row'][idx]['SAWS_TA_AVG']
                item['HD'] = res_json['RealtimeWeatherStation']['row'][idx]['SAWS_HD']
                item['WIND_CODE'] = int(res_json['RealtimeWeatherStation']['row'][idx]['CODE'])
                item['WIND_NAME_KR'] = res_json['RealtimeWeatherStation']['row'][idx]['NAME']
                item['WIND_NAME'] = ref.WIND_HEX_NAME[item['WIND_CODE']]
                item['WIND_SPEED_AVG'] = res_json['RealtimeWeatherStation']['row'][idx]['SAWS_WS_AVG']
                item['RAINFALL'] = res_json['RealtimeWeatherStation']['row'][idx]['SAWS_RN_SUM']
                item['SOLAR'] = res_json['RealtimeWeatherStation']['row'][idx]['SAWS_SOLAR']
                item['SHINE'] = res_json['RealtimeWeatherStation']['row'][idx]['SAWS_SHINE']
                item['OBS_DATE'] = res_json['RealtimeWeatherStation']['row'][idx]['SAWS_OBS_TM']
                item['lat'] = float(obs[find_idx+1].split(',')[1])
                item['lon'] = float(obs[find_idx+1].split(',')[2])
                self.__data.append(item)
        else:
            print('Parsing Error: {}'.format(result_code))
        '''
