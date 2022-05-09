import json

# Служебные слова
SERVICE_WORDS = [
    'ADMIT', 'ALLOCATABLE', 'ALLOCATE', 'ASSIGN', 'ASSIGNMENT', 'ATEND', 'BACKSPACE', 'BLOCKDATA',
    'CALL', 'CASE', 'CHARACTER', 'CLOSE', 'COMMON', 'COMPLEX', 'CONTAINS', 'CONTINUE',
    'CYCLY', 'DATA', 'DEALLOCATE', 'DEFAULT', 'DIMENSION', 'DO', 'DOUBLE', 'ELSE', 'END'
    'END PROGRAM', 'EXIT', 'EXTERNAL', 'FORMAT', 'FUNCTION', 'GO TO', 'IF', 'IMPLICIT', 'NONE',
    'INCLUDE', 'INQUIRE', 'INTEGER', 'INTENT', 'INTERFACE', 'INTRINSIC', 'LOGICAL', 'MAP', 'MODULE', 'NAMELIST',
    'NONE', 'OPEN', 'OPTIONAL', 'PARAMETER', 'PAUSE', 'POINTER', 'PRINT', 'WRITE', 'PRECISION',
    'ENDFILE', 'PROCEDURE', 'END IF', 'PROGRAM', 'ENTRY', 'EQUIVALENCE', 'READ', 'REAL', 'RECORD', 'RECURSIVE',
    'RETURN', 'REWIND', 'SAVE', 'STOP', 'STRUCTURE', 'SUBRCUTINE', 'TARGET', 'THEN', 'TYPE', 'UNION', 'USE', 'WHILE'
]

# Операции
OPERATIONS = ['*', '+', '-', '**', '.', '/', '=', '<', '<=', '<>', '=', '>', '>=', '::', '==', 'SQRT', 'AND', 'OR', 'FALSE',
              'TRUE', 'NOT']
# Разделители
SEPARATORS = ['\t', '\n', ' ', '(', ')', ',', '.', ':', ';', '[', ']']


# Каждому token_value(лексеме) ставит в соответсвие класс+код
def check(tokens, token_class, token_value):
    if not (token_value in tokens[token_class]):
        token_code = str(len(tokens[token_class]) + 1)  # Код токена
        tokens[token_class][token_value] = token_class + token_code  # Класс+код


# Получаем операцию
def get_operation(input_sequence, i):
    for k in range(3, 0, -1):  # Смотрим все операции от 3 символов и до 1
        if i + k < len(input_sequence):  # Проверяем, чтобы не был конец файла
            buffer = input_sequence[i:i + k]  # Помещаем буффер наши цепочку символов
            if buffer in OPERATIONS:  # Возвращаем, если это операция
                return buffer
    return ''


# Получаем разделитель
def get_separator(input_sequence, i):
    buffer = input_sequence[i]  # Записываем в буффер
    if buffer in SEPARATORS:  # Если есть, то возвращаем разделитель
        return buffer
    return ''


def main():
    # лексемы
    # I класс идентификаторов;
    # W класс служебных слов;
    # N или C класс констант (числовых или символьных);
    # O класс операций (одно-, дву- или многолитерных);
    # R класс разделителей (однолитерных или двулитерных).
    tokens = {'I': {}, 'W': {}, 'O': {}, 'R': {}, 'N': {}, 'C': {}}

    # Формируем коды служебных слов
    for service_word in SERVICE_WORDS:
        check(tokens, 'W', service_word)
    # Формируем коды операций
    for operation in OPERATIONS:
        check(tokens, 'O', operation)
    # Формируем коды разделителей
    for separator in SEPARATORS:
        check(tokens, 'R', separator)

    # файл, содержащий текст на входном языке программирования
    f = open('factorial.txt', 'r')
    input_sequence = f.read()  # Считываем файл
    f.close()  # Закрываем

    i = 0  # Переменная для итерации
    state = 'S'  # Начальное состояние
    output_sequence = buffer = ''  # Выход

    # Пока есть символы
    while i < len(input_sequence):
        symbol = input_sequence[i]  # Текущий символ
        operation = get_operation(input_sequence, i)
        separator = get_separator(input_sequence, i)

        # Если начальное состояние S
        if state == 'S':

            buffer = ''  # Буфер

            # Если встретили букву
            if symbol.isalpha():
                state = 'q1'
                buffer += symbol

            # Если встретили цифру
            elif symbol.isdigit():
                state = 'q3'
                buffer += symbol

            # Если встретили кавычки
            elif symbol == "\"":
                state = 'q9'
                buffer += symbol

            # Если встретили восклицательный знак
            elif symbol == '!':
                state = 'q10'

            # Если встретили операцию
            elif operation:
                check(tokens, 'O', operation)  # Добавили операцию если её нет
                output_sequence += tokens['O'][operation] + ' '  # Добавили в выходную последовательность
                i += len(operation) - 1  # Перешли к след символу

            # Если встретили разделитель
            elif separator:
                if separator != ' ':  # Если это не пробел
                    check(tokens, 'R', separator)  # Добавили разделитель если его нет
                    output_sequence += tokens['R'][separator]  # Добавили в выходную последовательность
                    if separator == '\n':  # Если новая строка
                        output_sequence += '\n'
                    else:
                        output_sequence += ' '  # Иначе пробел

            # Если конец файла
            elif i == len(input_sequence) - 1:
                state = 'Z'  # Конечное состояние

        # Если начальное состояние q1
        elif state == 'q1':
            # Если опять символ
            if symbol.isalpha():
                buffer += symbol  # Добавили в буффер

            # Если встретили цифру, то это идентификатор
            elif symbol.isdigit():
                state = 'q2'  # перешли в новое состояние
                buffer += symbol  # Добавили в буффер

            # Если это не цифра и не буква
            else:

                # Семантическая процедура 1
                if operation or separator:
                    if buffer in SERVICE_WORDS:
                        output_sequence += tokens['W'][buffer] + ' '
                    elif buffer in OPERATIONS:
                        output_sequence += tokens['O'][buffer] + ' '

                    # Семантическая процедура 2
                    else:
                        check(tokens, 'I', buffer)  # Проверили встречался ли раньше идентификатор
                        output_sequence += tokens['I'][buffer] + ' '  # Добавили в выходную последовательность

                    # Если встретили операцию
                    if operation:
                        check(tokens, 'O', operation)  # Добавили операцию если её нет
                        output_sequence += tokens['O'][operation] + ' '  # Добавили в выходную последовательность
                        i += len(operation) - 1  # Перешли к след символу

                    # Если встретили разделитель
                    elif separator:
                        if separator != ' ':  # Если это не пробел
                            check(tokens, 'R', separator)  # Добавили разделитель если его нет
                            output_sequence += tokens['R'][separator]  # Добавили в выходную последовательность
                            if separator == '\n':  # Если новая строка
                                output_sequence += '\n'
                            else:
                                output_sequence += ' '  # Иначе пробел
                state = 'S'  # перешли в начальное состояние

        # Если начальное состояние q2
        elif state == 'q2':
            # Если буква или цифра
            if symbol.isalnum():
                buffer += symbol  # Добавили в буффер
            else:
                # Семантическая процедура 2
                if operation or separator:
                    check(tokens, 'I', buffer)  # Проверили встречался ли раньше идентификатор
                    output_sequence += tokens['I'][buffer] + ' '  # Добавили в выходную последовательность
                    if operation:
                        check(tokens, 'O', operation)  # Добавили операцию если её нет
                        output_sequence += tokens['O'][operation] + ' '  # Добавили в выходную последовательность
                        i += len(operation) - 1  # Перешли к след символу
                    if separator:
                        if separator != ' ':  # Если это не пробел
                            check(tokens, 'R', separator)  # Добавили разделитель если его нет
                            output_sequence += tokens['R'][separator]  # Добавили в выходную последовательность
                            if separator == '\n':  # Если новая строка
                                output_sequence += '\n'
                            else:
                                output_sequence += ' '  # Иначе пробел
                    state = 'S'  # Переход в начальное состояние

        # Если начальное состояние q3
        elif state == 'q3':
            # Если цифра
            if symbol.isdigit():
                buffer += symbol  # Добавили в буффер
            # Если точка
            elif symbol == '.':
                state = 'q4'  # Перешли в новое состояние
                buffer += symbol  # Добавили в буффер
            # Если e или E
            elif symbol == 'e' or symbol == 'E':
                state = 'q6'  # Перешли в новое состояние
                buffer += symbol  # Добавили в буффер
            else:
                # Семантическая процедура 3
                if operation or separator:
                    check(tokens, 'N', buffer)  # Занесли числовую константу
                    output_sequence += tokens['N'][buffer] + ' '  # Добавили в выходную последовательность
                    if operation:
                        check(tokens, 'O', operation)  # Добавили операцию если её нет
                        output_sequence += tokens['O'][operation] + ' '  # Добавили в выходную последовательность
                        i += len(operation) - 1  # Перешли к след символу
                    if separator:
                        if separator != ' ':  # Если это не пробел
                            check(tokens, 'R', separator)  # Добавили разделитель если его нет
                            output_sequence += tokens['R'][separator]  # Добавили в выходную последовательность
                            if separator == '\n':  # Если новая строка
                                output_sequence += '\n'
                            else:
                                output_sequence += ' '  # Иначе пробел
                    state = 'S'  # Переход в начальное состояние

        # Если начальное состояние q4
        elif state == 'q4':
            # Проверили, что цифра
            if symbol.isdigit():
                state = 'q5'  # Перешли в новое состояние
                buffer += symbol  # Добавили в буффер

        # Если начальное состояние q5
        elif state == 'q5':
            # Если цифра
            if symbol.isdigit():
                buffer += symbol  # Добавили в буффер
            # Если e или E
            elif symbol == 'e' or symbol == 'E':
                state = 'q6'  # Перешли в новое состояние
                buffer += symbol  # Добавили в буффер
            else:
                # Семантическая процедура 3
                if operation or separator:
                    check(tokens, 'N', buffer)  # Занесли числовую константу
                    output_sequence += tokens['N'][buffer] + ' '  # Добавили в выходную последовательность
                    if operation:
                        check(tokens, 'O', operation)  # Добавили операцию если её нет
                        output_sequence += tokens['O'][operation] + ' '  # Добавили в выходную последовательность
                        i += len(operation) - 1  # Перешли к след символу
                    if separator:
                        if separator != ' ':  # Если это не пробел
                            check(tokens, 'R', separator)  # Добавили разделитель если его нет
                            output_sequence += tokens['R'][separator]  # Добавили в выходную последовательность
                            if separator == '\n':  # Если новая строка
                                output_sequence += '\n'
                            else:
                                output_sequence += ' '  # Иначе пробел
                    state = 'S'  # Перешли в начальное состояние

        # Если начальное состояние q6
        elif state == 'q6':
            # Если - или +
            if symbol == '-' or symbol == '+':
                state = 'q7'  # Перешли в новое состояние
                buffer += symbol  # Добавили в буффер
            # Если цифра
            elif symbol.isdigit():
                state = 'q8'  # Перешли в новое состояние
                buffer += symbol  # Добавили в буффер

        # Если начальное состояние q7
        elif state == 'q7':
            # Если цифра
            if symbol.isdigit():
                state = 'q8'  # Перешли в новое состояние
                buffer += symbol  # Добавили в буффер

        # Если начальное состояние q8
        elif state == 'q8':
            # Если цифра
            if symbol.isdigit():
                buffer += symbol  # Добавили в буффер
            else:
                # Семантическая процедура 3
                if operation or separator:
                    check(tokens, 'N', buffer)  # Занесли числовую константу
                    output_sequence += tokens['N'][buffer] + ' '  # Добавили в выходную последовательность
                    if operation:
                        check(tokens, 'O', operation)  # Добавили операцию если её нет
                        output_sequence += tokens['O'][operation] + ' '  # Добавили в выходную последовательность
                        i += len(operation) - 1  # Перешли к след символу
                    if separator:
                        if separator != ' ':  # Если это не пробел
                            check(tokens, 'R', separator)  # Добавили разделитель если его нет
                            output_sequence += tokens['R'][separator]  # Добавили в выходную последовательность
                            if separator == '\n':  # Если новая строка
                                output_sequence += '\n'
                            else:
                                output_sequence += ' '  # Иначе пробел
                state = 'S'  # Перешли в начальное состояние

        # Если начальное состояние q9
        elif state == 'q9':
            # Если символ не апостороф
            if symbol != "\"":
                buffer += symbol  # Добавили в буффер
            # Если символ апостроф
            elif symbol == "\"":
                buffer += symbol  # Добавили в буффер
                check(tokens, 'C', buffer)  # Добавили символьною константу если её нет
                output_sequence += tokens['C'][buffer] + ' '  # Добавили в выходную последовательность
                state = 'S'  # Перешли в начальное состояние

        # Если начальное состояние q10
        elif state == 'q10':
            # Если конец строки
            if symbol == '\n':
                state = 'S'
            # Если конец файла
            elif i == len(input_sequence) - 1:
                state = 'Z'

        i += 1  # Переходим к следующему символу

    # файлы, содержащие все таблицы лексем
    for token_class in tokens.keys():
        with open('%s.json' % token_class, 'w') as write_file:
            data = {val: key for key, val in tokens[token_class].items()}
            json.dump(data, write_file, indent=4)

    # файл, содержащий последовательность кодов лексем входной программы
    f = open('tokens.txt', 'w')  # Открыли для записи
    f.write(output_sequence)  # Записали выходную последовательность
    f.close()  # Закрыли файл


if __name__ == '__main__':
    main()
