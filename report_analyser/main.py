import tarfile
import sys
import os
import re
from Machine_config import Machine


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
