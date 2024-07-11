 #!/usr/bin/python3

import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
import json

# TTN MQTT settings
TTN_MQTT_BROKER = "eu1.cloud.thethings.network"
TTN_APP_ID = "your-app-id"
TTN_ACCESS_KEY = "your-access-key"

# InfluxDB settings
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "your-influxdb-token"
INFLUXDB_ORG = "your-org"
INFLUXDB_BUCKET = "your-bucket"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(f"v3/{TTN_APP_ID}/devices/+/up")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(f"Message received: {msg.payload.decode()}")
    data = json.loads(msg.payload.decode())
    
    # Parse the payload
    device_id = data['end_device_ids']['device_id']
    payload_fields = data['uplink_message']['decoded_payload']
    
    # Create a point and write to InfluxDB
    point = Point("sensor_data")\
        .tag("device", device_id)\
        .field("temperature", payload_fields['temperature'])\
        .field("humidity", payload_fields['humidity'])\
        .field("aqi", payload_fields['aqi'])\
        .field("tvoc", payload_fields['tvoc'])\
        .field("eco2", payload_fields['eco2'])
    
    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
    print(f"Data written to InfluxDB: {point}")

# Set up InfluxDB client
influxdb_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN)
write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

# Set up MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(TTN_APP_ID, TTN_ACCESS_KEY)
client.connect(TTN_MQTT_BROKER, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks, and handles reconnecting.
client.loop_forever()

