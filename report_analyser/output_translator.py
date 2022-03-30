import re

ansi = r'\x1b\[\d*[A-Z]*'


def translate_output(code):
    code = re.sub('\x07', '', code)  # Звук при ошибке. Точно в утиль
    #code = re.sub(r'\[root@\S* ~]# ', '', code)
    new_line = ''
    digit = ''
    state = 'standard'
    position = 0
    for letter in code:
        if state == 'standard':
            if letter == '\x1b':
                state = 'escape'
            elif letter == '\x08':
                position = max(0, position - 1)
            else:
                new_line = new_line[:position] + letter + new_line[position:]
                position += 1
        else:
            if letter == '[':
                pass
            elif '0' <= letter <= '9':
                digit += letter
            elif letter == 'K':
                new_line = ''
                digit = ''
                position = 0
                state = 'standard'
            elif letter == 'P':  # удаляет символы справа
                number = int(digit)
                #last_symbol = new_line[position - 1]
                digit = ''
                #position = max(0, position - 1)
                new_line = new_line[:position] + new_line[position + number:]
                #position += number
                state = 'standard'
            elif letter == '@':
                #pass
                #print('!')
                number = int(digit)
                digit = ''
                new_line = new_line[:position] + '^' * number + new_line[position + 1:]
                #position += number
                state = 'standard'
            else:
                raise ValueError()
    return new_line


#with open("test.txt") as t:
#    test = t.read()
test = '[root@05-router ~]# ip a a dev eth1 10.10.10.12/24\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x1b[1P'
#test = '[root@03-bridge ~]# ip link set vlan9 master br\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x087 master br\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08add dev br type bridge\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x1b[3Pset vlan7 master br\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08add link eth2 name vlan9 type vlan id 9\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x081 name vlan7 type vlan id 7'
line = test
print(line.__repr__())
print(translate_output(line).__repr__())
print(line)
print('-' * 30)
