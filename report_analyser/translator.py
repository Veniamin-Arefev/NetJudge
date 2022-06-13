"""REmove escape-sequences from text."""
import re


def translate(code: str) -> (str, str):
    """Translates text with bash escape sequences to normal text.

    Input: raw shell input.
    Ouput: tuple: (type of line, processed line without control sequences).
    """
    code = re.sub('\x07', '', code)  # Звук при ошибке. Не нужен
    code = re.sub(r'(\s|\S)*:\t', '', code)  # Удаление tab-ов
    """Removing color sequences"""
    try:
        code = re.sub(r'\x1b\[\d*m', '', code)
        code = re.sub(r'\x1b\[\d*;\d*m\*', '', code)
        code = re.sub(r'\x1b\[\d*;\d*;\d*;\d*m', '', code)
    except Exception:
        pass
    new_line = ''
    digit = ''
    state = 'standard'
    position = 0
    line_type = 'input' if (re.search(r'\[[\s|\S]*~\]#', code) or
                            re.search(r'\(reverse-i-search\)`[\s |\S]*\':', code) or
                            re.search(r'\[[\s|\S]*~\]\$', code)) \
        else 'output'

    if line_type == 'input':
        code = re.sub(r'\S*\[[\s|\S]*~\]# ', '', code)  # иногда в начале бывают лишние символы
        code = re.sub(r'\(reverse-i-search\)`[\s |\S]*\':', '', code)
    for letter in code:
        if state == 'standard':
            if letter == '\x1b':
                state = 'escape'
            elif letter == '\x08':
                position = max(0, position - 1)
            else:
                new_line = new_line[:position] + letter + new_line[position + 1:]
                position += 1
        else:
            if letter == '[':  # начало управляющей последовательности
                pass
            elif '0' <= letter <= '9':
                digit += letter
            elif letter == 'K':
                digit = ''
                if not digit or (number := int(digit)) == 0:
                    new_line = new_line[:position]
                elif number == 1:
                    new_line = new_line[position:]
                    position = 0
                else:
                    new_line = ''
                    position = 0
                state = 'standard'
            elif letter == 'P':  # удаляет символы справа
                number = int(digit)
                digit = ''
                new_line = new_line[:position] + new_line[position + number:]
                state = 'standard'
            elif letter == '@':
                number = int(digit)
                digit = ''
                new_line = new_line[:position] + chr(1234) * number + new_line[position:]
                state = 'standard'
            else:
                return line_type, 'WARNING: UNPARSED ' + code

    if new_line and new_line[-1] == '\r':
        new_line = new_line[:-1]
        new_line = re.sub(r'(\s|\S)*\r', '', new_line)  # \r - это еще и возврат каретки
        new_line = re.sub(r'\[[\s|\S]*~\]\$', '', new_line)
    return line_type, new_line.strip()
