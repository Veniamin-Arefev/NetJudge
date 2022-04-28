import re
import shlex
from . import ip_parser
from .CONSTANTS import *


class Machine:
    class Interface:
        def __init__(self, ip, state='down'):
            self.ip = ip
            self.state = state

        def __repr__(self):
            return self.ip + ', state: ' + self.state

    class Vlan:
        def __init__(self, interface=None, id=None, master=None):
            self.master = master
            self.interface = interface

        def __repr__(self):
            return f"Interface: {self.interface}, master: {self.master}"

    def __init__(self, name, number, code):
        self.name = name
        self.number = number
        self.devices = {}
        self.ip_rules = []
        self.ip_routes = []  # from, via, table, priority, -1 == unknown
        self.is_router = False
        self.unknown_lines = []
        self.vlans = {}
        for line in code:
            if line[0] == 'input':
                if line == 'exit':  # конец ввода
                    break
                res = self.parse_line(line[1])
                if not res:
                    self.unknown_lines.append((line, res), )

    def parse_line(self, line):
        """Checks line correctness
        Also completes device's configuration
        basing on command text
        """
        if '\t' in line:  # костыль для проверки работоспособности
            return False
        args = shlex.split(line)
        if args[0] == 'ip':
            return ip_parser.parse_ip(self, args[1:])
        elif 'sysctl'.startswith(args[0]):  # пока нет автодополнения
            if line.replace(' ', '') == 'sysctlnet.ipv4.ip_forward=1':
                # Пробелы могут быть и не быть в разных местах. Так проще
                self.is_router = True
                return True
            else:
                return False
        elif re.fullmatch(r'for \w+ in `ls /sys/class/net`; do ip link set dev \$\w+ up; done', line.strip()):
            self.is_router = True
            return True
        elif args[0] == 'ping':  # параметры вроде -c1 нам вряд ли нужны
            return re.fullmatch(ip_regexp, args[-1]) is not None
        elif args[0] == 'tcpdump':
            return True
        elif args[0] == 'exit':
            return True
    
    def print_log(self):
        print('Name: ', self.name)
        print('devices: ', self.devices)
        print('routes: ', self.ip_routes)
        print('vlans: ', self.vlans)
        print('is_router: ', self.is_router)
        print('unsupported commands: ')
        if self.unknown_lines:
            for line in self.unknown_lines:
                print(f"    {line}")
        print('-' * 30)
