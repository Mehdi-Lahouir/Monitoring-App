import requests
import random
import time
import uuid
from dal import IotDeviceDao

class HttpIoTDevice:
    def __init__(self, server_url, endpoint):
        self.server_url = server_url
        self.endpoint = endpoint
        self.mac_address = self.get_mac_address()

    def send_data(self, temperature):
        payload = {'mac_address': self.mac_address, 'temperature': temperature}
        response = requests.post(self.server_url + self.endpoint, json=payload)
        print(f'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS{response}')

        print(f"Response Content: {response.content}")
        print(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            print(f"Temperature sent via HTTP: {temperature}")
        else:
            print(f"Failed to send temperature. Status code: {response.status_code}")

    def start_sending(self):
        try:
            while True:
                temperature = round(random.uniform(20, 30), 2)
                self.send_data(temperature)

                self.insert_data_to_database(self.mac_address, temperature)

                time.sleep(5)
        except KeyboardInterrupt:
            print("Script terminated by user")

    def get_mac_address(self):
        return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(5, -1, -1)])

    def insert_data_to_database(self, mac, temp, id=1):
        IotDeviceDao.create_iot_device(id, mac, temp)


if __name__ == "__main__":
    SERVER_URL = 'http://127.0.0.1:8008'
    HTTP_ENDPOINT = '/iot/temperature'

    http_device = HttpIoTDevice(SERVER_URL, HTTP_ENDPOINT)
    s = http_device.get_mac_address() 
    print(f"MAC Address: {s}")
    http_device.start_sending()