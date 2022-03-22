import tarfile
import sys
import os
import re
from translator import translate


class Machine:
    def __init__(self, name, number, code):
        self.ip_addresses = None
        self.name = name
        self.number = number
        self.code = code
        self.get_ip()

    def get_ip(self):
        ip_addr = re.findall(r'ip a\S{0,6}[ ]+a\S{0,2}[ ]+dev[ ]+eth\d[ ]+\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,3}', self.code)
        self.ip_addresses = dict()
        for ip in ip_addr:
            self.ip_addresses[re.search(r'eth\d', ip)[0]] = re.search(r'\d{,3}.\d{1,3}.\d{1,3}.\d{1,3}/\d{1,2}', ip)[0]

    def __repr__(self):
        return f"Machine number {self.number}, name {self.name}, ip_addresses: \n{self.ip_addresses}"



machines = dict()
file_path = sys.argv[1]  # пока так
file_names = [file for file in os.listdir(file_path) if
              re.fullmatch(r"report.\d+.\S+", file)]
for name in file_names:
    number = re.search(r"\d+", name)[0]
    machine_name = name[len('report') + len(number[0]) + 3:]
    obj = tarfile.open(file_path + '/' + name)
    obj_members = obj.getmembers()
    text = obj.extractfile('./IN.txt').read().decode()
    machines[machine_name + number] = Machine(machine_name, number, translate(text))
for machine in machines.values():
    print(machine)
