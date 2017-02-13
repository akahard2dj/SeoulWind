from apscheduler.schedulers.blocking import BlockingScheduler
from Crawler.SeoulDataAPI.seoul_openapi_crwaler import *
from Crawler.db.db import *

import datetime

class DBWraping:
    def __init__(self, sqlite_db_fname):
        self.__db_fname = sqlite_db_fname
        self.__info = Info2JsonSeoul('parameters.txt')
        self.__db = AirInfoDB(sqlite_db_fname)
        self.__data = None

    def __get_info_data(self):
        self.__data = self.__info.gather_data()

    def pushing_data_to_db(self):
        self.__get_info_data()
        self.__db.insert_data(self.__data)


class CrawlerSchedule:
    def __init__(self, **kwargs):
        self.__INTERVAL = 1
        try:
            self.__INTERVAL = kwargs['interval']
        except KeyError:
            pass

        self.schedule = BlockingScheduler()

    def schedule_job(self):
        DBWraping('seoul_air.db').pushing_data_to_db()
        print(datetime.datetime.now().time())

    def add_job(self):
        self.schedule.add_job(self.schedule_job, 'interval', minutes=30)

    def start(self):
        self.schedule.start()

if __name__ == '__main__':
    schedule = CrawlerSchedule()
    schedule.add_job()
    try:
        schedule.start()
    except (KeyboardInterrupt, SystemExit):
        exit(0)
