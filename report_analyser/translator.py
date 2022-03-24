import re


def translate(code):
    """Translates text with bash escape sequences to normal text

    Input: raw shell input
    Return: list of commands without escape sequences
    Leaves \x04 and \t in lines, to process them in main part
    """

    for letter in 'A', 'B', 'C', 'D':
        code = code.replace(f"[{letter}", f"\x1b[{letter}\x1b")
    code = code.replace('\x7f', '\x1b\x7f\x1b')
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
            symbol_number = 0
            for word in data:
                if word == '[A':  # переход на предыдущую строку
                    index -= 1
                    if index < 0:
                        index = len(new_lines) - 1  # вроде бы пойдет по кругу
                        current_line = new_lines[index]
                        symbol_number = len(current_line)
                    else:
                        current_line = new_lines[index]
                        symbol_number = len(current_line)
                elif word == '[B':  # переход на следующую строку
                    index += 1
                    if index >= len(new_lines):
                        current_line = ''
                        symbol_number = 0
                        index = len(new_lines)
                    else:
                        current_line = new_lines[index]
                        symbol_number = len(current_line)
                elif word == '[D':  # сдвиг курсора влево
                    symbol_number -= 1
                    symbol_number = max(0, symbol_number)
                elif word == '[C':  # сдвиг курсора вправо
                    symbol_number += 1
                    if symbol_number > len(current_line):
                        symbol_number = len(current_line)
                elif word == '\x7f':  # удаление символа
                    symbol_number -= 1
                    if symbol_number < 0:
                        symbol_number = 0
                    else:  # нужно, так как возможна ошибка пользователя, при которой он нажимает
                        # del, находясь в начале
                        # строки, перед всеми символами. Тогда ничего не удаляется
                        current_line = current_line[:symbol_number] + \
                                       current_line[symbol_number + 1:]
                elif word in ('\t', '\x04'):
                    pass
                else:  # не ESCAPE-SEQ -> часть текста
                    current_line = current_line[:symbol_number] + word + \
                                   current_line[symbol_number:]
                    symbol_number += len(word)  # заведомо не выйдет в ноль
            new_lines.append(current_line)
            line_number += 1
    return new_lines