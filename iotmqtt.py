import paho.mqtt.client as mqtt
import random
import time
import uuid
from dal import IotDeviceDao
class MqttIoTDevice:
    def __init__(self, broker_url, broker_port, topic):
        self.broker_url = broker_url
        self.broker_port = broker_port
        self.topic = topic
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.mac_address = self.get_mac_address()

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
                print(f"Temperature published via MQTT: {temperature}")
                self.insert_data_to_database(self.mac_address, temperature)

                time.sleep(5)
        except KeyboardInterrupt:
            print("Script terminated by user")
            self.client.disconnect()

    def get_mac_address(self):
        return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(5, -1, -1)])
    
    def insert_data_to_database(self, mac, temp):
        IotDeviceDao.create_iot_device(1, mac, temp)
if __name__ == "__main__":
    MQTT_BROKER_URL = 'test.mosquitto.org'
    MQTT_BROKER_PORT = 1883
    MQTT_TOPIC = 'iot/temperature'
  
    mqtt_device = MqttIoTDevice(MQTT_BROKER_URL, MQTT_BROKER_PORT, MQTT_TOPIC)
    s = mqtt_device.get_mac_address() 
    print(f"MAC Address: {s}")
    mqtt_device.connect()
    mqtt_device.start_sending()