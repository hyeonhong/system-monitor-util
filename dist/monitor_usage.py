#!/usr/bin/env python3
import psutil
import os
import math
import json
from pprint import pprint


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 1)
    return "%s %s" % (s, size_name[i])


def monitor_usage():
    # JSON object
    jsonObj = {}

    # Get CPU usage
    count = 0
    cpu_usage = 0
    for x in range(3):
        percentage = psutil.cpu_percent(interval=1)
        count = count + 1
        # print(f'cpu usage #{count}: {str(percentage)}')
        cpu_usage = cpu_usage + percentage

    cpu_usage = round(cpu_usage / 3, 2)
    jsonObj['cpu_usage'] = str(cpu_usage) + '%'

    # Get memory usage
    mem = psutil.virtual_memory()
    available = mem.available
    available_in_GB = convert_size(available)
    # print(f'{available} bytes = {available_in_GB} GiB')
    jsonObj['memory_usage'] = available_in_GB

    # Get disk usage
    partition_info = psutil.disk_partitions()
    for disk in partition_info:
        disk_free = psutil.disk_usage(disk.mountpoint).free
        usage_percent = psutil.disk_usage(disk.mountpoint).percent
        jsonObj[f'disk {disk.mountpoint}'] = convert_size(disk_free) + ' ' + str(usage_percent) + '%'

    # Write to JSON file
    ip = os.environ['IP']
    print(f'IP address: {ip}')
    with open(f'{ip}.json', 'w', encoding='utf-8') as json_file:
        json.dump(jsonObj, json_file, ensure_ascii=False)

    # Print to console
    pprint(jsonObj)
    print('Successfully executed the file: monitor_usage.py')


def main():
    monitor_usage()


if __name__ == '__main__':
    main()
