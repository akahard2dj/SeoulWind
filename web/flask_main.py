from flask import Flask, render_template
from flask import g
import sqlite3
import json

DATABASE = '../seoul_air.db'

app = Flask(__name__)
app.config['CACHE_TYPE'] = "null"


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)

    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def get_latest_time(query):
    cur = get_db().execute(query)
    rv = cur.fetchall()
    date_list = list()
    for idx in range(len(rv)):
        date_list.append(rv[idx][0])

    set_data = list(set(date_list))
    set_data.sort(reverse=True)

    return set_data[0]


def db_to_json(db_data, data_type):
    res_list = list()
    for db_item in db_data:
        item = dict()
        item['time'] = db_item[0]
        item['name'] = db_item[1]
        item['coordinates'] = [db_item[2], db_item[3]]
        item['wind'] = [db_item[4], db_item[5]]
        if not data_type == 'wind':
            item[data_type] = db_item[6]
        if item[data_type] == 0.0:
            pass
        else:
            res_list.append(item)

    return json.dumps(res_list)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def main_page():
    return render_template('index.html')


@app.route('/test/')
def test_page():
    return render_template('test_air.html', data_type='wind', data_sample='/data/current/wind')


@app.route('/test_pm25/')
def test_pm25page():
    return render_template('test_air_pm25.html')


@app.route('/map/current/<data_type>')
def redirect_page(data_type):

    json_url = '/data/current/' + data_type
    return render_template('test_air.html', data_type=data_type, data_sample=json_url)


@app.route('/data/current/<data_type>', methods=['POST', 'GET'])
def show_data_type_page(data_type):
    pre_defined_keyword = ['wind', 'hum', 'temp', 'pm25', 'pm10', 'no2', 'so2', 'co', 'o3']
    try:
        idx_res = pre_defined_keyword.index(data_type)
    except ValueError:
        return '404'

    latest_date = get_latest_time('select time_measurement from air_info')

    if idx_res == 0:
        data = list(query_db('select time_measurement, obs_name, coord_x, coord_y, wind_x, wind_y, air_hum from air_info where time_measurement ="{}"'.format(latest_date)))
    else:
        data = list(query_db('select time_measurement, obs_name, coord_x, coord_y, wind_x, wind_y, air_{} from air_info  where time_measurement ="{}"'
                        .format(pre_defined_keyword[idx_res], latest_date)))
    res_json = db_to_json(data, data_type)
    return res_json


@app.route('/d3/')
def d3_page():
    return render_template('d3.html')

if __name__ == '__main__':
    app.run()
