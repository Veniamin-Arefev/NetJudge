import re
from .CONSTANTS import *


def parse_ip(config, args):
    """Ip command analyser"""
    if 'address'.startswith(args[0]):  # пустых аргументов здесь быть не должно. Добавить такую проверку
        return ip_address(config, args[1:])
    elif args[0].startswith('r'):
        if 'route'.startswith(args[0]):  # ip r -> ip route
            return ip_route(config, args[1:])
        elif 'rule'.startswith(args[0]):
            return ip_rule(config, args)
        else:
            return False
    elif 'link'.startswith(args[0]):
        return ip_link(config, args[1:])


def ip_address(config, args):
    """Parses ip address command
    Returns True if command is correct
    """
    if 'add'.startswith(args[0]):  # ip addr add ...
        if not 'dev'.startswith(args[1]):
            return False
        dev = args[2]
        ip_addr = args[3]  # можно и без маски
        if not re.fullmatch(ip_regexp, ip_addr):
            return False
        state = config.devices[dev].state if dev in config.devices.keys() else 'down'
        config.devices[dev] = config.Interface(ip_addr, state)
        return True
    elif 'delete'.startswith(args[0]):  # ip addr del ...
        if not 'dev'.startswith(args[1]):
            return False
        dev = args[2]
        config.devices[dev] = ('No_ip_yet', 'down')
        return True


def ip_route(config, args):
    """Analyser for ip route command"""
    if not args:  # просто ip route, показ информации
        return True
    if 'default'.startswith(args[1]):  # объединять нельзя, может быть автодополнение
        route_from = 'default'
    elif re.fullmatch(ip_regexp, args[1]):
        route_from = args[1]
    else:
        return False
    if 'delete'.startswith(args[0]):
        config.ip_routes = [route for route in config.ip_routes
                            if routr[0] != route_from]
        return True
    elif 'add'.startswith(args[0]):
        if not 'via'.startswith(args[2]) or not re.fullmatch(ip_regexp, args[3]):
            return False
        config.ip_routes.append((route_from, args[3], -1, -1))
        if len(args) > 4:
            return config.add_table_priority(args[4:])
        return True


def add_table_priority(config, args):
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
    modified = config.ip_routes[-1]  # гарантируется, что команда вызывается
    # только при добавлении правила
    # то есть всегда для последнего правила
    config.ip_routes[-1] = (modified[0], modified[1], table, priority)
    return True


def ip_rule(config, args):
    pass


def ip_link(config, args):
    """ip link subcommand for ip analyser"""
    if 'set'.startswith(args[0]):  # так быть не должно, не реализована часть команд
        return ip_link_set(config, args[1:])
    elif 'add'.startswith(args[0]):
        return ip_link_add(config, args[1:])
    else:
        return False


def ip_link_set(config, args):
    """ip link set subfunction"""
    if len(args) >= 2 and args[-1] in ('up', 'down'):  # отрицательные индексы так как слово dev можно опускать
        if args[-2] in config.devices.keys():
            config.devices[args[-2]].state = args[-1]
        else:
            config.devices[args[-2]] = config.Interface('No_ip_yet', args[-1])
        return True
    elif args[1] == 'master':
        if len(args) != 3:
            return False
        if args[0] in config.vlans.keys():
            config.vlans[args[0]].master = args[2]
        else:
            config.vlans[args[0]] = config.Vlan(master=args[2])
        return True
    else:
        return False


def ip_link_add(config, args):  # Работает только с добавлением vlan-ов
    """Ip link add subfunction"""
    print('add!', args)
    if len(args) != 8:
        return False
    if not 'link'.startswith(args[0]):
        return False
    if not re.fullmatch('eth\d', args[1]):
        return False
    interface = args[1]
    if not 'name'.startswith(args[2]):
        return False
    name = args[3]
    if not 'type'.startswith(args[4]) or \
            not args[5] == 'vlan' or \
            not 'id'.startswith(args[6]) or \
            not args[7].isdigit():
        return False
    vlan_id = int(args[7])
    config.vlans[name] = config.Vlan(interface=interface, id=vlan_id)
    return True
