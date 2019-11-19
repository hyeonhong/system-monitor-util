#!/usr/bin/env python3
import os
import sys
import time
import json
import csv
import paramiko
from multiprocessing.dummy import Pool as ThreadPool


def collect_stat(ip, username, key_filepath):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # Connect to host via SSH
        print(f'Connecting to {ip} via SSH ...')
        client.connect(ip, username=username, key_filename=key_filepath)
    except Exception as e:
        print(e)
        sys.exit(1)

    print(f'Connection established successfully')

    # Copy local directory 'dist' to remote directory 'monitor_usage'
    sftp = client.open_sftp()
    remote_directory = 'monitor_usage'
    try:
        sftp.mkdir(remote_directory)
    except IOError:
        print("Error: The 'monitor_usage' directory already exists")

    # single level copy
    for filename in os.listdir('dist'):
        local_path = os.path.join('dist', filename)
        remote_path = os.path.join(remote_directory, filename)

        if os.path.isfile(local_path):
            sftp.put(local_path, remote_path)
            sftp.chmod(remote_path, 0o777)
        else:
            raise Exception('A directory cannot be copied')

    # Load the bash config files so that the system PATH is recognized
    pre_command = '''
    . ~/.profile;
    . ~/.bash_profile;
    '''

    # Execute the shell script
    print('Executing the shell script ...')
    stdin, stdout, stderr = client.exec_command(f'{pre_command} export IP="{ip}"; sh ./{remote_directory}/script.sh')
    std_output = ''.join(stdout.readlines())
    error_output = ''.join(stderr.readlines())
    if error_output:
        print('stderr:\n' + error_output)
    if std_output:
        print('stdout:\n' + std_output)

    # Download the result file
    time.sleep(1)
    remote_path = os.path.join(remote_directory, f'{ip}.json')
    local_path = os.path.join('result', f'{ip}.json')
    sftp.get(remote_path, local_path)

    # Delete the remote directory
    stdin, stdout, stderr = client.exec_command(f'rm -rf {remote_directory}')
    std_output = ''.join(stdout.readlines())
    error_output = ''.join(stderr.readlines())
    if error_output:
        print('stderr:\n' + error_output)
    if std_output:
        print('stdout:\n' + std_output)

    sftp.close()
    client.close()


def main():
    # Get the path for key file
    with open('key_path.conf') as f:
        content = f.readlines()
    key_filepath = content[0].strip()

    """Start threading"""

    # make the Pool of workers
    pool = ThreadPool(5)

    jobs = [
        ('10.28.7.7', 'centos', key_filepath),
        ('10.28.7.77', 'centos', key_filepath),
        ('10.28.7.137', 'centos', key_filepath),
        ('10.28.7.197', 'centos', key_filepath),
        ('10.28.3.199', 'winflex', key_filepath)
    ]

    pool.starmap(collect_stat, jobs)  # results are not assigned to variable since there's no return value in collect_stat

    """End threading"""

    # Combine multiple JSON files to one CSV file
    header = [
        "IP_address",
        "cpu_usage",
        "memory_usage",
        "disk /",
        "disk /data"
    ]
    with open('result.csv', 'w', encoding='utf-8', newline='') as csv_file:
        writer = csv.writer(csv_file)

        # Write the column header for CSV file
        writer.writerow(header)

        # Write the values to CSV file
        for filename in os.listdir('result'):
            filepath = os.path.join('result', filename)
            with open(filepath, 'r', encoding='utf-8') as read_file:
                if filename.endswith('json'):
                    jsonObj = json.load(read_file)
                    row_value = [
                        filename[:-5],
                        jsonObj["cpu_usage"],
                        jsonObj["memory_usage"],
                        jsonObj["disk /"],
                        jsonObj["disk /data"]
                    ]

                    writer.writerow(row_value)

    # Write summary to console
    print('\x1b[6;30;42m' + 'Summary' + '\x1b[0m')
    with open("result.csv", newline='') as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header
        print(header)
        data = [r for r in reader]  # put the terminals in list
        ws1 = next((terminal for terminal in data if terminal[0] == '10.28.7.7'), None)
        ws2 = next((terminal for terminal in data if terminal[0] == '10.28.7.77'), None)
        was1 = next((terminal for terminal in data if terminal[0] == '10.28.7.137'), None)
        was2 = next((terminal for terminal in data if terminal[0] == '10.28.7.197'), None)
        test = next((terminal for terminal in data if terminal[0] == '10.28.3.199'), None)
        print(ws1, ws2, was1, was2, test, sep='\n')
        # data = sorted(data)  # sort by first element(ip_address) of list
        # print('\n'.join(str(v) for v in data))  # print list


if __name__ == '__main__':
    main()
