import tarfile
import sys
import os
import re
from translator import translate


def get_ip(line):
    """Returns all ip addresses initialised in line"""
    ip_addr = re.findall(r'ip a\S{0,6}[ ]+a\S{0,2}[ ]+dev[ ]+eth\d[ ]+'
                         r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,3}', line)
    ip_addresses = {}
    for ip in ip_addr:
        ip_addresses[re.search(r'eth\d', ip)[0]] = \
            re.search(r'\d{,3}.\d{1,3}.\d{1,3}.\d{1,3}/\d{1,2}', ip)[0]
    return ip_addresses


class Machine:
    def __init__(self, name, number, text):
        self.ip_addresses = None
        self.name = name
        self.number = number
        self.lines = translate(text)

    def __repr__(self):
        return f"Machine number {self.number}, name {self.name}," \
               f" ip_addresses: \n{self.ip_addresses}"


file_path = sys.argv[1]  # пока так
file_names = [file for file in os.listdir(file_path) if
              re.fullmatch(r"report.\d+.\S+", file)]

machines = {}
for name in file_names:
    number = re.search(r"\d+", name)[0]
    machine_name = name[len('report') + len(number[0]) + 3:]
    obj = tarfile.open(file_path + '/' + name)
    obj_members = obj.getmembers()
    text = obj.extractfile('./IN.txt').read().decode()
    machines[machine_name + number] = Machine(machine_name, number, text)
