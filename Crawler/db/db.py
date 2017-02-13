import sqlite3


class AirInfoDB:
    def __init__(self, db_file):
        self.__dbfile = db_file
        self.__table = 'air_info'
        self.con = None
        self.cur = None
        self.init_db()

    def init_db(self):
        self.con = self.create_connection()
        self.cur = self.con.cursor()

        if not self.is_table_exists():
            self.create_table()

    def create_connection(self):
        try:
            con = sqlite3.connect(self.__dbfile)
            return con
        except sqlite3.DatabaseError as e:
            print('{}'.format(e))

        return None

    def create_table(self):
        self.cur.execute('''
            CREATE TABLE air_info(
            id INTEGER PRIMARY KEY,
            obs_name text,
            time_measurement text,
            coord_x text,
            coord_y text,
            wind_x real,
            wind_y real,
            air_hum real,
            air_temp real,
            air_pm25 real,
            air_pm10 real,
            air_no2 real,
            air_so2 real,
            air_co real,
            air_o3 real)
        ''')

    def is_table_exists(self):
        self.cur.execute("select name from sqlite_master where type='table' and name='{}'".format(self.__table))
        res = list(self.cur)
        if not res:
            return False
        else:
            return True

    def insert_data(self, json_data):
        item_to_db = list()
        check_time = None
        for item in json_data:
            check_time = item['timestamp']
            datas = (item['name'], item['timestamp'], item['coordinates'][0], item['coordinates'][1],
                    item['wind'][0], item['wind'][1], item['hum'], item['temp'], item['pm25'], item['pm10'],
                    item['no2'], item['so2'], item['co'], item['o3'])
            item_to_db.append(datas)

        self.cur.execute('SELECT rowid from {} where time_measurement = "{}"'.format(self.__table, check_time))
        check_data = self.cur.fetchall()

        if len(check_data) == 0:
            self.cur.executemany('INSERT INTO {}(obs_name, time_measurement,  coord_x, coord_y, wind_x, wind_y, air_hum, air_temp, air_pm25, air_pm10, air_no2, air_so2, air_co, air_o3)'
                                 ' values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'.format(self.__table),
                                item_to_db)
        else:
            print('Already parsing on {}'.format(check_time))

        self.con.commit()
        

    def testquery(self):
        self.cur.execute("select * from air_info")
        print(self.cur.fetchall())
