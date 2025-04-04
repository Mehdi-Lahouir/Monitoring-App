# dal.py
import hashlib
from typing import List, Any
from models import User,  Device, DeviceUsage,IotDevice
from typing import Any
from dbConnection import mydb
from werkzeug.security import generate_password_hash

class UserDao:
    @staticmethod
    def get_user_by_id(user_id: int) -> User:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        return User(**result) if result else None

    @staticmethod
    def get_user_by_username(username: str) -> User:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()
        return User(**result) if result else None

    @staticmethod
    def authenticate_user(username_or_email: str, password: str) -> dict:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user WHERE username = %s OR email = %s", (username_or_email, username_or_email))
        result = cursor.fetchone()
        cursor.close()

        if result and result['password_hash'] == password:
            return result  
        return None

    @staticmethod
    def create_user(username: str, password_hash: str, email: str) -> bool:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("INSERT INTO user (username, password_hash, email) VALUES (%s, %s, %s)", (username, password_hash, email))
        mydb.commit()
        cursor.close()

        return True

    @staticmethod
    def delete_user(user_id: int) -> bool:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("DELETE FROM user WHERE user_id = %s", (user_id,))
        mydb.commit()
        cursor.close()
        return True
    
    @staticmethod
    def signup_user(username: str, password: str, email: str) -> User:
        password_hash = generate_password_hash(password)

        cursor = mydb.cursor(dictionary=True)
        cursor.execute("INSERT INTO user (username, password_hash, email) VALUES (%s, %s, %s)", (username, password_hash, email))
        mydb.commit()
        
        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()

        return User(**result) if result else None
    
    @staticmethod
    def update_password(user_id: int, new_password: str) -> bool:
        new_password_hash = hashlib.sha256(new_password.encode('utf-8')).hexdigest()

        cursor = mydb.cursor(dictionary=True)
        cursor.execute("UPDATE user SET password_hash = %s WHERE id = %s", (new_password_hash, user_id))
        mydb.commit()
        cursor.close()

        return True
class DeviceDao:
    @staticmethod
    def get_device_by_ip(ip_address: str) -> Device:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM device WHERE ip_address = %s", (ip_address,))
        result = cursor.fetchone()
        cursor.close()
        return Device(**result) if result else None

    @staticmethod
    def get_all_devices() -> List[Device]:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM device")
        result = cursor.fetchall()
        cursor.close()
        return [Device(**row) for row in result]

    @staticmethod
    def create_device(user_id: int, name: str, ip_address: str, mac_address: str, longitude: float, latitude: float) -> Device:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("INSERT INTO device (user_id, name, ip_address, mac_address, longitude, latitude) VALUES (%s, %s, %s, %s, %s, %s)",
                    (user_id, name, ip_address, mac_address, longitude, latitude))
        mydb.commit()
        cursor.close()
        return Device(user_id=user_id, name=name, ip_address=ip_address, mac_address=mac_address, longitude=longitude, latitude=latitude)

    @staticmethod
    def delete_device(ip_address: str) -> bool:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("DELETE FROM device WHERE ip_address = %s", (ip_address,))
        mydb.commit()
        cursor.close()
        return True

    @staticmethod
    def get_devices_by_user(user_id: int) -> List[Device]:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM device WHERE user_id = %s", (user_id,))
        result = cursor.fetchall()
        cursor.close()
        return [Device(**row) for row in result]
    


class DeviceUsageDao:
    @staticmethod
    def get_device_usage_by_id(usage_id: int) -> DeviceUsage:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM device_usage WHERE id = %s", (usage_id,))
        result = cursor.fetchone()
        cursor.close()
        return DeviceUsage(**result) if result else None

    @staticmethod
    def get_all_device_usages() -> List[DeviceUsage]:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM device_usage")
        result = cursor.fetchall()
        cursor.close()
        return [DeviceUsage(**row) for row in result]

    @staticmethod
    def get_device_usages_by_device(ip_address: str) -> List[DeviceUsage]:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM device_usage WHERE device_ip_address = %s", (ip_address,))
        result = cursor.fetchall()
        cursor.close()
        return [DeviceUsage(**row) for row in result]

    @staticmethod
    def create_device_usage(device_ip_address: str, cpu_usage: float, ram_usage: float, disk_usage: float) -> bool:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("INSERT INTO device_usage (device_ip_address, cpu_usage, ram_usage, disk_usage) VALUES (%s, %s, %s, %s)",
                       (device_ip_address, cpu_usage, ram_usage, disk_usage))
        mydb.commit()
        cursor.close()
        return True

class IotDeviceDao:
    @staticmethod
    def get_iot_device_by_id(device_id: int) -> IotDevice:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM iot_device WHERE id = %s", (device_id,))
        result = cursor.fetchone()
        cursor.close()
        return IotDevice(**result) if result else None

    @staticmethod
    def get_all_iot_devices() -> List[IotDevice]:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM iot_device")
        result = cursor.fetchall()
        cursor.close()
        return [IotDevice(**row) for row in result]

    @staticmethod
    def get_iot_devices_by_user(user_id: int) -> List[IotDevice]:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM iot_device WHERE user_id = %s", (user_id,))
        result = cursor.fetchall()
        cursor.close()
        return [IotDevice(**row) for row in result]

    @staticmethod
    def create_iot_device(user_id: int, mac: str, temp: float) -> bool:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("INSERT INTO iot_device (user_id, mac, temp) VALUES (%s, %s, %s)",
                    (user_id, mac, temp))
        mydb.commit()
        cursor.close()
        return True



    @staticmethod
    def delete_iot_device(device_id: int) -> bool:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("DELETE FROM iot_device WHERE id = %s", (device_id,))
        mydb.commit()
        cursor.close()
        return True
    
    @staticmethod
    def get_iot_device_by_mac(mac_address: str) -> List[IotDevice]:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM iot_device WHERE mac = %s", (mac_address,))
        result = cursor.fetchall()
        cursor.close()
        return [IotDevice(**row) for row in result]
    
IotDeviceDao.get_iot_device_by_mac('98:54:1b:eb:5a:e1')