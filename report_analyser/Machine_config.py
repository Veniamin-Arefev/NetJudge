import re
import shlex
from translator import translate


class Machine:
    def __init__(self, name, number, text):
        self.name = name
        self.number = number
        self.devices = {}
        self.ip_rules = []
        self.ip_routes = []
        code_lines = translate(text)
        for line in code_lines:
            self.parse_line(line)

    class Interface:
        def __init__(self, name, state='down'):
            self.name = name
            self.state = state

    def parse_line(self, line):
        """Checks line correctness
        Also completes device's configuration
        basing on command text
        """
        args = shlex.split(line)
        if args[0] == 'ip':
            return self.parse_ip(args[1:])


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
            ip_addr = args[3]
            if not re.fullmatch(r'\d{,3}.\d{1,3}.\d{1,3}.\d{1,3}/\d{1,2}', ip_addr):
                return False
            self.devices[dev] = self.Interface(ip_addr)
            return True
        elif 'delete'.startswith(args[0]):  # ip addr del ...
            if not 'dev'.startswith(args[1]):
                return False
            dev = args[2]
            self.devices.pop(dev)
            return True

    def ip_route(self, args):
        pass

    def ip_rule(self, args):
        pass

    def ip_link(self, args):
        """ip link subcommand for ip analyser"""
        if not 'set'.startswith(args[0]):
            return False
        elif not 'device'.startswith(args[1]):
            return False
        elif not re.fullmatch(r'eth\d', args[2]):
            return False
        elif args[3] in ('up', 'down'):
            if not args[2] in self.devices.keys():
                self.devices[args[2]] = self.Interface('No_ip_yet')
            self.devices[args[2]].state = args[3]
            return True
        else:
            return False

#Machine1 = Machine('name', 1, 'line')
#print(Machine1.parse_line('ip link set dev eth1 up'))
#while (line := input()) != '\x04':
#    if Machine1.parse_line(line):
#        print('OK')
#    else:
#        print('NO')