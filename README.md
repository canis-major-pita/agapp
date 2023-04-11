# agapp

Basic app for fleet vehicle data monitoring
Python app using REST API

Flask is a prerequisite, install to your environment with 'pip install Flask'

Run program with 'python agapp.py'

<h2>Instructions on use: </h2>

POST to <code>http://localhost:5000/register_sensor</code> with JSON data {"sensor_id": 1, "vin": "VIN123"} to register a sensor.</br>
POST to <code>http://localhost:5000/add_sensor_data</code> with JSON data {"sensor_id": 1, "metric": "RPM", "value": 1000, "timestamp": "2023-04-09T12:00:00"} to add sensor data.</br>
GET <code>http://localhost:5000/query_sensors?vin=VIN123&metrics=RPM&metrics=speed&start_date=2023-04-03T00:00:00&end_date=2023-04-10T00:00:00</code> to query sensor data.</br>

Replace prefilled fields with the relevant data.  VIN numbers must be 17 alphanumeric characters to be accepted as a valid VIN. 
