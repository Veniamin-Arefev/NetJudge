import re
import shlex
from translator import translate


class Machine:

    ip_regexp = r'\d{,3}.\d{1,3}.\d{1,3}.\d{1,3}(/\d\d?)?'

    def __init__(self, name, number, text):
        self.name = name
        self.number = number
        self.devices = {}
        self.ip_rules = []
        self.ip_routes = []  # from, via, table, priority, -1 == unknown
        self.is_router = False
        code_lines = translate(text)
        for line in code_lines:
            if line == '\x04':  # конец ввода
                break
            self.parse_line(line)

    class Interface:
        def __init__(self, ip, state='down'):
            self.ip = ip
            self.state = state

        def __repr__(self):
            return self.ip + ' ' + self.state

    def parse_line(self, line):
        """Checks line correctness
        Also completes device's configuration
        basing on command text
        """
        args = shlex.split(line)
        if args[0] == 'ip':
            return self.parse_ip(args[1:])
        elif 'sysctl'.startswith(args[0]):  # пока нет автодополнения
            if line.replace(' ', '') == 'sysctlnet.ipv4.ip_forward=1':
                self.is_router = True
                return True
            else:
                return False


    def parse_ip(self, args):
        """Ip command analyser"""
        if 'address'.startswith(args[0]):  # пустых аргументов здесь быть не должно. Добавить такую проверку
            return self.ip_address(args[1:])
        elif args[0].startswith('r'):
            if 'route'.startswith(args[0]):  # ip r -> ip route
                return self.ip_route(args[1:])
            elif 'rule'.startswith(args[0]):
                return self.ip_rule(args)
            else:
                return False
        elif 'link'.startswith(args[0]):
            return self.ip_link(args[1:])


    def ip_address(self, args):
        """Parses ip address command
        Returns True if command is correct
        """
        if 'add'.startswith(args[0]):  # ip addr add ...
            if not 'dev'.startswith(args[1]):
                return False
            dev = args[2]
            if not re.fullmatch(r'eth\d', dev):
                return False
            ip_addr = args[3]  # можно и без маски
            if not re.fullmatch(Machine.ip_regexp, ip_addr):
                return False
            state = self.devices[dev].state if dev in self.devices.keys() else 'down'
            self.devices[dev] = self.Interface(ip_addr, state)
            return True
        elif 'delete'.startswith(args[0]):  # ip addr del ...
            if not 'dev'.startswith(args[1]):
                return False
            dev = args[2]
            self.devices[dev] = ('No_ip_yet', 'down')
            return True

    def ip_route(self, args):
        """Analyser for ip route command"""
        if not args:  # просто ip route, показ информации
            return True
        if 'default'.startswith(args[1]):  # объединять нельзя, может быть автодополнение
            route_from = 'default'
        elif re.fullmatch(Machine.ip_regexp, args[1]):
            route_from = args[1]
        else:
            return False
        if 'delete'.startswith(args[0]):
            self.ip_routes = [route for route in self.ip_routes
                              if routr[0] != route_from]
        elif 'add'.startswith(args[0]):
            if not 'via'.startswith(args[2]) or not re.fullmatch(Machine.ip_regexp, args[3]):
                return False
            self.ip_routes.append((route_from, args[3], -1, -1))
            if len(args) > 4:
                self.add_table_priority(args[4:])

    def add_table_priority(self, args):
        """Adds table number and priority to ip rule/route commands"""
        table = -1
        priority = -1
        if 'table'.startswith(args[0]):
            table = args[1]
        elif 'priority'.startswith(args[0]):
            priority = args[1]
        else:
            return False
        if len(args) > 2:
            if 'table'.startswith(args[2]):
                table = args[3]
            elif 'priority'.startswith(args[2]):
                priority = args[3]
            else:
                return False
        modified = self.ip_routes[-1]  # гарантируется, что команда вызывается
        # только при добавлении правила
        # то есть всегда для последнего правила
        self.ip_routes[-1] = (modified[0], modified[1], table, priority)

    def ip_rule(self, args):
        pass

    def ip_link(self, args):
        """ip link subcommand for ip analyser"""
        if not 'set'.startswith(args[0]):  # так быть не должно, не реализована часть команд
            return False
        elif not 'device'.startswith(args[1]):
            return False
        elif not re.fullmatch(r'eth\d', args[2]):
            return False
        elif args[3] in ('up', 'down'):
            self.devices[args[2]] = self.Interface('No_ip_yet', args[3])
            return True
        else:
            return False
