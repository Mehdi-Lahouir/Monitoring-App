import requests
import random
import time
import uuid
from dal import IotDeviceDao

class HttpIoTDevice:
    def __init__(self, mac, server_url, endpoint, id):
        self.server_url = server_url
        self.id = id
        self.endpoint = endpoint
        self.mac_address = mac
        self.running = False 

    def send_data(self, temperature):
        payload = {'mac_address': self.mac_address, 'temperature': temperature}
        response = requests.post(self.server_url + self.endpoint, json=payload)

        if response.status_code == 200:
            print(f"Temperature sent via HTTP: {temperature}")
        else:
            print(f"Failed to send temperature. Status code: {response.status_code}")

    def start_sending(self):
        self.running = True
        try:
            while self.running:
                temperature = round(random.uniform(20, 30), 2)
                self.send_data(temperature)
                self.insert_data_to_database(self.mac_address, temperature, self.id)
                time.sleep(5)
        except KeyboardInterrupt:
            print("Script terminated by user")

    def stop_sending(self):
        self.running = False

    def insert_data_to_database(self, mac, temp, id):
        IotDeviceDao.create_iot_device(id, mac, temp)

if __name__ == "__main__":
    SERVER_URL = 'http://127.0.0.1:8008'
    HTTP_ENDPOINT = '/iot/temperature'

    http_device = HttpIoTDevice('',SERVER_URL, HTTP_ENDPOINT, 1)
    http_device.start_sending()

