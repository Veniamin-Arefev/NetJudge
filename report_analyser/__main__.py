import tarfile
import sys
import os
import re
from report_analyser.input_checker.Machine_config import Machine
from .translator import translate


if __name__ == '__main__':
    file_pathes = sys.argv[1:]
    for file_path in file_pathes:
        file_names = [file for file in os.listdir(file_path) if
                      re.fullmatch(r"report.\d+.\S+", file)]
        machines = {}
        for name in file_names:
            number = re.search(r"\d+", name)[0]
            machine_name = name[len('report') + len(number[0]) + 3:]
            obj = tarfile.open(file_path + '/' + name)
            obj_members = obj.getmembers()
            text = obj.extractfile('./OUT.txt').read().decode()
            text = re.sub('\r', '', text)  # re.split работал не совсем так, как надо
            lines = [translate(line) for line in text.split('\n') if line]
            machines[machine_name + number] = Machine(machine_name, number, lines)
        print(f'Task number: {int(number)}')
        for machine in machines.values():
            print('Name: ', machine.name)
            print('devices: ', machine.devices)
            print('routes: ', machine.ip_routes)
            print('is_router: ', machine.is_router)
            print('unsupported commands: ')
            if machine.unknown_lines:
                for line in machine.unknown_lines:
                    print(f"    {line}")
            print('-' * 30)
        if len(file_pathes) > 1:
            print('\n' + '*' * 30 + '\n')
