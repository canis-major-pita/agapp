# -*- coding: utf-8 -*-
"""

"""

from flask import Flask, request, jsonify
import datetime
import sqlite3
from collections import defaultdict

app = Flask(__name__)


def setup_database():
    try:
        conn = sqlite3.connect('fleet.db')
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensors (
                id INTEGER PRIMARY KEY,
                vin TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY,
                sensor_id INTEGER,
                metric TEXT,
                value REAL,
                timestamp TEXT,
                FOREIGN KEY (sensor_id) REFERENCES sensors (id)
            )
        ''')

        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error setting up database: {e}")

setup_database()


class Sensor:
    def __init__(self, sensor_id, vin):
        self.sensor_id = sensor_id
        self.vin = vin
        self.data = defaultdict(list)

    def add_data(self, metric, value):
        self.data[metric].append(value)

    def get_average(self, metric, start_date, end_date):
        filtered_data = [x for x in self.data[metric] if start_date <= x[1] <= end_date]
        if not filtered_data:
            return None

        return sum(x[0] for x in filtered_data) / len(filtered_data)

class Fleet:
    def __init__(self):
        self.sensors = {}
    
    def is_valid_vin(vin):
        return len(vin) == 17 and vin.isalnum()

    def register_sensor(sensor_id, vin):
        if not fleet.is_valid_vin(vin):
            return 'Invalid VIN. VIN must be 17 characters long and contain only alphanumeric characters.'
        try:
            conn = sqlite3.connect('fleet.db')
            cursor = conn.cursor()
    
            cursor.execute('SELECT * FROM sensors WHERE id=?', (sensor_id,))
            if cursor.fetchone():
                return 'Sensor with this ID already exists.'
    
            cursor.execute('INSERT INTO sensors (id, vin) VALUES (?, ?)', (sensor_id, vin))
            conn.commit()
            conn.close()
            return 'Sensor registered successfully.'
        except sqlite3.Error as e:
            return f"Error registering sensor: {e}"

    def add_sensor_data(sensor_id, metric, value, timestamp):
        conn = sqlite3.connect('fleet.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO sensor_data (sensor_id, metric, value, timestamp) VALUES (?, ?, ?, ?)', (sensor_id, metric, value, timestamp.isoformat()))
        conn.commit()
        conn.close()


    def query_sensors(vin=None, metrics=None, start_date=None, end_date=None):
        conn = sqlite3.connect('fleet.db')
        cursor = conn.cursor()
    
        if not start_date:
            start_date = datetime.datetime.now() - datetime.timedelta(days=1)
        if not end_date:
            end_date = datetime.datetime.now()
        if not metrics:
            metrics = []
    
        results = {}
        for metric in metrics:
            query = '''
                SELECT AVG(value) as average
                FROM sensor_data
                JOIN sensors ON sensors.id = sensor_data.sensor_id
                WHERE metric = ? AND timestamp >= ? AND timestamp <= ?
            '''
    
            query_params = [metric, start_date.isoformat(), end_date.isoformat()]
    
            if vin:
                query += " AND sensors.vin = ?"
                query_params.append(vin)
    
            cursor.execute(query, query_params)
            result = cursor.fetchone()
            if result[0] is not None:
                results[metric] = result[0]
    
        conn.close()
        return results


fleet = Fleet()
fleet.register_sensor(1, 'VIN123')
fleet.register_sensor(2, 'VIN456')

fleet.add_sensor_data(1, 'RPM', 1000, datetime.datetime.now() - datetime.timedelta(days=5))
fleet.add_sensor_data(1, 'RPM', 2000, datetime.datetime.now() - datetime.timedelta(days=3))
fleet.add_sensor_data(1, 'speed', 40, datetime.datetime.now() - datetime.timedelta(days=5))
fleet.add_sensor_data(1, 'speed', 60, datetime.datetime.now() - datetime.timedelta(days=3))

fleet.add_sensor_data(2, 'RPM', 1500, datetime.datetime.now() - datetime.timedelta(days=7))
fleet.add_sensor_data(2, 'RPM', 2500, datetime.datetime.now() - datetime.timedelta(days=1))
fleet.add_sensor_data(2, 'speed', 50, datetime.datetime.now() - datetime.timedelta(days=7))
fleet.add_sensor_data(2, 'speed', 70, datetime.datetime.now() - datetime.timedelta(days=1))

start_date = datetime.datetime.now() - datetime.timedelta(days=7)
end_date = datetime.datetime.now()

print(fleet.query_sensors(vin='VIN123', metrics=['RPM', 'speed'], start_date=start_date, end_date=end_date))

fleet = Fleet()

@app.route('/register_sensor', methods=['POST'])
def register_sensor_route():
    sensor_id = request.json['sensor_id']
    vin = request.json['vin']
    result = fleet.register_sensor(sensor_id, vin)
    if result == 'Sensor registered successfully.':
        return {'result': 'success'}
    else:
        return {'result': 'error', 'message': result}

@app.route('/add_sensor_data', methods=['POST'])
def add_sensor_data_route():
    sensor_id = request.json['sensor_id']
    metric = request.json['metric']
    value = request.json['value']
    timestamp = datetime.datetime.fromisoformat(request.json['timestamp'])
    fleet.add_sensor_data(sensor_id, metric, value, timestamp)
    return {'result': 'success'}

@app.route('/query_sensors', methods=['GET'])
def query_sensors_route():
    vin = request.args.get('vin')
    metrics = request.args.getlist('metrics')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if start_date:
        start_date = datetime.datetime.fromisoformat(start_date)
    if end_date:
        end_date = datetime.datetime.fromisoformat(end_date)

    result = fleet.query_sensors(vin=vin, metrics=metrics, start_date=start_date, end_date=end_date)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)