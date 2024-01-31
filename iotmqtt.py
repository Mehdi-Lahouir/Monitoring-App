import paho.mqtt.client as mqtt
import random
import time
from dal import IotDeviceDao

class MqttIoTDevice:
    def __init__(self, mac, broker_url, broker_port, topic, id):
        self.broker_url = broker_url
        self.broker_port = broker_port
        self.id = id
        self.topic = topic
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.mac_address = mac

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker")
        else:
            print(f"Connection failed with code {rc}")

    def connect(self):
        self.client.connect(self.broker_url, self.broker_port)

    def start_sending(self):
        self.client.loop_start()
        try:
            while True:
                temperature = round(random.uniform(20, 30), 2)
                payload = {'mac_address': self.mac_address, 'temperature': temperature}
                self.client.publish(self.topic, str(payload))
                self.insert_data_to_database(self.mac_address, temperature, self.id)

                time.sleep(5)
        except KeyboardInterrupt:
            print("Script terminated by user")
            self.stop_sending()

    def stop_sending(self):
        self.client.disconnect()

    def insert_data_to_database(self, mac, temp, id):
        IotDeviceDao.create_iot_device(id, mac, temp)

if __name__ == "__main__":
    MQTT_BROKER_URL = 'test.mosquitto.org'
    MQTT_BROKER_PORT = 1883
    MQTT_TOPIC = 'iot/temperature'

    mqtt_device = MqttIoTDevice(MQTT_BROKER_URL, MQTT_BROKER_PORT, MQTT_TOPIC, 1)
    mqtt_device.connect()
    mqtt_device.start_sending()

    # To stop the MQTT device after a certain condition or time, you can use:
    # mqtt_device.stop_sending()
