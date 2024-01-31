from dataclasses import dataclass

@dataclass
class Device():
    name: str
    user_id:int
    ip_address: str
    mac_address: str
    longitude: float
    latitude: float


@dataclass
class DeviceUsage():
    id: int
    device_id: int
    cpu_usage: float
    ram_usage: float
    disk_usage: float
    def __init__(self, id, device_ip_address, cpu_usage, ram_usage, disk_usage):
        self.id = id
        self.device_ip_address = device_ip_address
        self.cpu_usage = cpu_usage
        self.ram_usage = ram_usage
        self.disk_usage = disk_usage


@dataclass
class IotDevice():
    id: int
    user_id: int
    mac: str
    temp: float
    timestamp: str  
    latitude: float
    longitude: float



@dataclass
class User():
    id: int
    username: str
    password_hash: str
    email: str

