from datetime import datetime
import subprocess
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from dal import DeviceUsageDao

def snmpwalk(oid,ip):
    result = subprocess.run(['snmpwalk', '-v2c', '-c', 'public', ip, oid], capture_output=True, text=True)

    storage_info = {}
    for line in result.stdout.splitlines():
        parts = line.split('=', 1)
        if len(parts) == 2:
            oid, value = parts
            oid = oid.strip()
            value = value.strip().replace('STRING: ', '')
            storage_info[oid] = value

    return storage_info

def snmpget(oid,ip):
    result = subprocess.run(['snmpget', '-v2c', '-c', 'public', ip, oid], capture_output=True, text=True)
    
    parts = result.stdout.split(':')
    
    if len(parts) >= 2:
        value = ''.join(parts[1:]).strip()
        numeric_value = ''.join(c for c in value if c.isdigit())
        if numeric_value:
            return int(numeric_value)
    return None

def find_index_by_description(description,ip):
    storage_info = snmpwalk('HOST-RESOURCES-MIB::hrStorageDescr',ip)
    for oid, desc in storage_info.items():
        if desc == description :
            index = int(oid.split('.')[-1])
            return index
        
def find_index_by_description2(description,ip):
    storage_info = snmpwalk('HOST-RESOURCES-MIB::hrStorageDescr',ip)
    for oid, desc in storage_info.items():
        if desc.startswith(description):
            index = int(oid.split('.')[-1])
            return index

    return None

def calculate_storage_size_gb(size_oid, allocation_units_oid,ip):
    size_result = subprocess.run(['snmpget', '-v2c', '-c', 'public', ip, size_oid], capture_output=True, text=True)
    allocation_units_result = subprocess.run(['snmpget', '-v2c', '-c', 'public', ip, allocation_units_oid], capture_output=True, text=True)
    size_value_str = size_result.stdout.split(':')[-1].strip()
    allocation_units_str = allocation_units_result.stdout.split(':')[-1].split()[0].strip()
    size_value = int(size_value_str)
    allocation_units = int(allocation_units_str)
    size_gb = (size_value * allocation_units) / (1024 ** 3)
    return size_gb

def calculate_storage_usage_percentage(used_oid, total_oid):

    if used_oid is not None and total_oid is not None and total_oid != 0:
        usage_percentage = (used_oid / total_oid) * 100
        return usage_percentage
    else:
        return None

def find_root_or_drives_indices(ip):
    indices = []

    root_filesystem_index = find_index_by_description('/',ip)
    if root_filesystem_index is not None:
        indices.append(root_filesystem_index)

    drive_c_index = find_index_by_description2('C:\\',ip)
    if drive_c_index is not None:
        indices.append(drive_c_index)

    drive_d_index = find_index_by_description2('D:\\',ip)
    if drive_d_index is not None:
        indices.append(drive_d_index)

    return indices

def snmp_def(ip,drive_labels,usage_percentages):
    root_or_drives_indices = find_root_or_drives_indices(ip)
    if root_or_drives_indices:
        for index in root_or_drives_indices:
            drive_labels.append(f"DISK{index}")
            root_or_drive_size_oid = f'HOST-RESOURCES-MIB::hrStorageSize.{index}'
            root_or_drive_allocation_units_oid = f'HOST-RESOURCES-MIB::hrStorageAllocationUnits.{index}'
            root_or_drive_used_oid = f'HOST-RESOURCES-MIB::hrStorageUsed.{index}'

            root_or_drive_size_gb = calculate_storage_size_gb(root_or_drive_size_oid, root_or_drive_allocation_units_oid,ip)
            used_value = calculate_storage_size_gb(root_or_drive_used_oid,root_or_drive_allocation_units_oid,ip )
            root_or_drive_usage_percentage = calculate_storage_usage_percentage(used_value, root_or_drive_size_gb)
            usage_percentages.append(root_or_drive_usage_percentage)
            
    else: pass

    ram_index = find_index_by_description('Physical memory',ip)
    if ram_index is not None:
        ram_size_oid = f'HOST-RESOURCES-MIB::hrStorageSize.{ram_index}'
        drive_labels.append("RAM")

        ram_allocation_units_oid = f'HOST-RESOURCES-MIB::hrStorageAllocationUnits.{ram_index}'
        ram_used_oid = f'HOST-RESOURCES-MIB::hrStorageUsed.{ram_index}'
        ram_size_gb = calculate_storage_size_gb(ram_size_oid, ram_allocation_units_oid,ip)
        used_value = calculate_storage_size_gb(ram_used_oid, ram_allocation_units_oid,ip)
        ram_usage_percentage = calculate_storage_usage_percentage(used_value, ram_size_gb)
        usage_percentages.append(ram_usage_percentage)

    else:
        ram_index = find_index_by_description('Physical Memory',ip)
        if ram_index is not None:
            drive_labels.append("RAM")

            ram_size_oid = f'HOST-RESOURCES-MIB::hrStorageSize.{ram_index}'
            ram_allocation_units_oid = f'HOST-RESOURCES-MIB::hrStorageAllocationUnits.{ram_index}'
            ram_used_oid = f'HOST-RESOURCES-MIB::hrStorageUsed.{ram_index}'
            ram_size_gb = calculate_storage_size_gb(ram_size_oid, ram_allocation_units_oid,ip)
            used_value = calculate_storage_size_gb(ram_used_oid, ram_allocation_units_oid,ip)
            ram_usage_percentage = calculate_storage_usage_percentage(used_value, ram_size_gb)
            usage_percentages.append(ram_usage_percentage)

        else:
            pass
    virtual_memory_index = find_index_by_description('Virtual memory',ip)
    if virtual_memory_index is not None:
        drive_labels.append("VM")
        virtual_memory_size_oid = f'HOST-RESOURCES-MIB::hrStorageSize.{virtual_memory_index}'
        virtual_memory_allocation_units_oid = f'HOST-RESOURCES-MIB::hrStorageAllocationUnits.{virtual_memory_index}'
        virtual_memory_used_oid = f'HOST-RESOURCES-MIB::hrStorageUsed.{virtual_memory_index}'

        virtual_memory_size_gb = calculate_storage_size_gb(virtual_memory_size_oid, virtual_memory_allocation_units_oid,ip)
        used_value = calculate_storage_size_gb(virtual_memory_used_oid,virtual_memory_allocation_units_oid,ip)
        virtual_memory_usage_percentage = calculate_storage_usage_percentage(used_value, virtual_memory_size_gb)
        usage_percentages.append(virtual_memory_usage_percentage)
    else:
        virtual_memory_index = find_index_by_description('Virtual Memory',ip)
        if virtual_memory_index is not None:
            drive_labels.append("VM")
            virtual_memory_size_oid = f'HOST-RESOURCES-MIB::hrStorageSize.{virtual_memory_index}'
            virtual_memory_allocation_units_oid = f'HOST-RESOURCES-MIB::hrStorageAllocationUnits.{virtual_memory_index}'
            virtual_memory_used_oid = f'HOST-RESOURCES-MIB::hrStorageUsed.{virtual_memory_index}'
            
            virtual_memory_size_gb = calculate_storage_size_gb(virtual_memory_size_oid, virtual_memory_allocation_units_oid,ip)
            used_value = calculate_storage_size_gb(virtual_memory_used_oid,virtual_memory_allocation_units_oid,ip)
            virtual_memory_usage_percentage = calculate_storage_usage_percentage(used_value, virtual_memory_size_gb)
            usage_percentages.append(virtual_memory_usage_percentage)
        else: pass

    user_cpu, system_cpu, idle_cpu = get_cpu_statistics(ip)
    if user_cpu is not None and system_cpu is not None and idle_cpu is not None:
        total_cpu = user_cpu + system_cpu + idle_cpu
        if total_cpu == 0:
            total_cpu = 1
            idle_cpu = 1
        cpu_usage_percentage = (total_cpu - idle_cpu) / total_cpu * 100
        drive_labels.append("CPU")
        usage_percentages.append(cpu_usage_percentage)

def get_cpu_statistics(ip):
    user_cpu_percentage = snmpget('.1.3.6.1.4.1.2021.11.9.0',ip)
    system_cpu_percentage = snmpget('.1.3.6.1.4.1.2021.11.10.0',ip)
    idle_cpu_percentage = snmpget('.1.3.6.1.4.1.2021.11.11.0',ip)
    
    return user_cpu_percentage, system_cpu_percentage, idle_cpu_percentage

def get_name(ip):
    name = snmpwalk('.1.3.6.1.2.1.1.5.0',ip)

    for oid, name in name.items():
        return name

def database(ip, drive_labels, usage_percentages):
    cpu_index = None
    ram_index = None
    disk_indices = []

    for index, label in enumerate(drive_labels):
        if label.startswith('DISK'):
            disk_indices.append(index)
        elif label == 'CPU':
            cpu_index = index
        elif label == 'RAM':
            ram_index = index

    if len(disk_indices) >= 2:
        sum_disk = sum(usage_percentages[i] for i in disk_indices)
        average_disk = sum_disk / len(disk_indices)

        for i in reversed(disk_indices):
            drive_labels.pop(i)
            usage_percentages.pop(i)

        drive_labels.append('DISK')
        usage_percentages.append(round(average_disk, 2))
    else:
        disk_index = disk_indices[0] if disk_indices else None

    cpu_usage = round(usage_percentages[cpu_index], 2) if cpu_index is not None else None
    ram_usage = round(usage_percentages[ram_index], 2) if ram_index is not None else None
    disk_usage = round(usage_percentages[disk_index], 2) if disk_index is not None else None
    DeviceUsageDao.create_device_usage(ip,cpu_usage,ram_usage,disk_usage)


def graph(ip):
    try:
        drive_labels = []
        usage_percentages = []
        snmp_def(ip, drive_labels, usage_percentages)
        
        plt.figure(figsize=(10, 6))
        plt.bar(drive_labels, usage_percentages, color='blue')
        plt.xlabel('Drive Label')
        plt.ylabel('Usage Percentage (%)')
        plt.title('Usage Percentage of Root Drives')
        plt.ylim(0, 100)

        image_stream = BytesIO()
        plt.savefig(image_stream, format='png')
        image_stream.seek(0)
        image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

        plt.close()

        return image_base64 , drive_labels , usage_percentages
    except Exception as e:
        return f"Failed to retrieve information from {ip}. Error: {str(e)}"

def history(ip):
    device_usages = DeviceUsageDao.get_device_usages_by_device(ip)

    device_usages.sort(key=lambda x: x.id)

    ids = [usage.id for usage in device_usages]
    cpu_usages = [usage.cpu_usage for usage in device_usages]
    ram_usages = [usage.ram_usage for usage in device_usages]
    disk_usages = [usage.disk_usage for usage in device_usages]

    plt.figure(figsize=(10, 6))
    plt.plot(ids, cpu_usages, marker='o', label='CPU Usage')
    plt.plot(ids, ram_usages, marker='o', label='RAM Usage')
    plt.plot(ids, disk_usages, marker='o', label='Disk Usage')

    plt.xlabel('ID')
    plt.ylabel('Usage Percentage (%)')
    plt.title('Historical Usage Data')
    plt.ylim(0, 100)
    
    plt.xticks(ids)
    plt.legend()
    plt.grid(True)

    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)
    image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

    plt.close()

    return image_base64
