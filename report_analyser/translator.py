import re

def translate(code: str) -> str:
    '''Translates text with shell escape sequences to normal text'''
    code = code.replace('\x7f', '\x1b' + chr(1234))  # так будет проще их обработать
    lines = re.split(r'[\r\n]', code)
    new_lines = []
    line_number = 0
    for line in lines:
        data = [elem for elem in re.split(r'\x1b', line) if elem]
        if not data or len(data) == 0:
            continue
        if len(data) == 1:
            new_lines.append(data[0])
            line_number += 1
        else:
            current_line = ''
            index = line_number
            symbol_number = 0  # по умолчанию смотрим на последний символ
            for word in data:
                if word == '[A':  # переход на предыдущую строку
                    index -= 1
                    if index < 0:
                        current_line = ''
                        symbol_number = 0
                    else:
                        current_line = new_lines[index]
                        symbol_number = len(current_line) - 1
                elif word == '[B':  # переход на следующую строку
                    index += 1
                    if index >= len(new_lines):
                        current_line = ''
                        symbol_number = 0
                    else:
                        current_line = new_lines[index]
                        symbol_number = len(current_line) - 1
                elif word == '[D':  # сдвиг курсора влево
                    symbol_number -= 1
                elif word == '[C':  # сдвиг курсора вправо
                    symbol_number += 1
                elif word.startswith(chr(1234)):  # удаление символа
                    begin = current_line[:symbol_number]
                    mid = word[1:]
                    end = current_line[symbol_number + 1:]
                    current_line = begin + mid + end  # удаление может быть в середине и с добавлением символа
                    symbol_number += len(word[1:]) - 1
            new_lines.append(current_line)
    return '\n'.join(new_lines)
