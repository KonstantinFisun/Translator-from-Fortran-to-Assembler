import lab1
import json
import re
import sys

# лексемы
tokens = {'W': {}, 'I': {}, 'O': {}, 'R': {}, 'N': {}, 'C': {}}

# файлы, содержащие все таблицы лексем
for token_class in tokens.keys():
    with open('%s.json' % token_class, 'r') as read_file:
        data = json.load(read_file)
        tokens[token_class] = data

# файл, содержащий последовательность кодов лексем входной программы
f = open('tokens.txt', 'r')
input_sequence = f.read()
f.close()

regexp = '[' + '|'.join(tokens.keys()) + ']' + '\d+'  # [W|I|O|R|N|C]\d+
match = re.findall(regexp, input_sequence)  # Оставили только лексемы

i = -1  # индекс разбираемого символа
nxtsymb = None  # разбираемый символ
row_counter = 1  # счётчик строк


# обработка ошибочной ситуации
def error(str):
    print('Ошибка в строке', row_counter)
    print(str)
    sys.exit()


# помещение очередного символа в nxtsymb
def scan():
    global i, nxtsymb, row_counter
    i += 1
    for token_class in tokens.keys():  # Идем по классам лексем
        if match[i] in tokens[token_class]:  # Если наша лексема нашлась
            nxtsymb = tokens[token_class][match[i]]  # Записали значение лексемы в nxtsymb
    if nxtsymb == '\n':  # Если это новая строчка
        row_counter += 1  # Прибавили к счетчику
        scan()  # Сканируем дальше


# программа
def program():
    scan()  # Считали новый символ
    if nxtsymb != "PROGRAM": error("Ожидалось PROGRAM")  # Если встретили не PROGRAM, то ошибка
    scan()  # Считали новый символ
    if not (name()): error("Не встречен идентификатор")  # Если встретили не идентификатор, то ошибка
    program = nxtsymb # Название программы
    scan() # Считали новый символ
    if nxtsymb != "IMPLICIT": error("Ожидалось IMPLICIT") # Если не встретили IMPLICIT
    scan() # Считали новый символ
    if nxtsymb != "NONE": error("Ожидалось NONE") # Если не встретили NONE
    operators()
    scan()
    if nxtsymb != program: error("Программа не закончена корректным именем")

# операторы
def operators():
    global i
    scan()
    while name() or \
            nxtsymb in ['SUBROUTINE', 'IF', 'DO', 'CALL', 'GOTO',
                        'CONTINUE', 'RETURN', 'PRINT']:
        operator() # Встретили оператор

        if nxtsymb == '}':
            break


# оператор
def operator():
    if name():
        scan()
        if nxtsymb == ':':
            scan()
            operator()
        elif nxtsymb == '(':
            scan()
            expression()
            while nxtsymb == ',':
                scan()
                expression()
            if nxtsymb != ')': error()
            scan()
        elif nxtsymb == '[':
            scan()
            expression()
            if nxtsymb != ']': error()
            scan()
        elif nxtsymb == '=':
            scan()
            expression()
        else:
            error()
    elif nxtsymb == 'SUBROUTINE': # Встретили функцию
        function()
    elif nxtsymb == 'IF': # Встретили IF
        conditional_operator()
    elif nxtsymb == 'WHILE': # Встретили WHILE
        while_loop()
    elif nxtsymb == 'DO': # Встретили DO
        do_while_loop()
    elif nxtsymb == 'GOTO': # Встретили GOTO
        goto_statement()
        scan()
    elif nxtsymb == 'CONTINUE': # Встретили CONTINUE
        continue_operator()
        scan()
    elif nxtsymb == 'RETURN':
        return_operator()
    elif nxtsymb == 'PRINT':
        print_operator()
    else:
        error("Некорректный оператор")


# имя (идентификатор)
def name():
    return nxtsymb in tokens['I'].values()  # Если идентификатор есть в лексема -> TRUE


# функция
def function():
    if nxtsymb != 'SUBROUTINE': error("Ожидалось SUBROUTINE")
    scan()
    if not (name()): error("Некорректный идентификатор")
    scan()


# выражение
def expression():
    if nxtsymb == '(':
        scan()
        expression()
        if nxtsymb != ')': error("Не встречено '('")
        scan()
    elif name():
        scan()
        if nxtsymb == '(':
            scan()
            expression()
            while nxtsymb == ',':
                scan()
                expression()
            if nxtsymb != ')': error("Не встречено '('")
            scan()
        elif nxtsymb == '[':
            scan()
            expression()
            while nxtsymb == ',':
                scan()
                expression()
            if nxtsymb != ']': error("Не встречено ']'")
            scan()
    elif number() or line():
        scan()
    else:
        error("Некорректное выражение")
    if arithmetic_operation():
        scan()
        expression()


# число (числовая константа)
def number():
    return nxtsymb in tokens['N'].values() # Если число есть в лексеме -> TRUE


# целое число (числовая константа)
def integer():
    return nxtsymb in tokens['N'].values() # Если число есть в лексеме -> TRUE


# вещественное число (числовая константа)
def real_number():
    return nxtsymb in tokens['N'].values() # Если число есть в лексеме -> TRUE


# строка (символьная константа)
def line():
    return nxtsymb in tokens['C'].values() # Если строка есть в лексеме -> TRUE


# переменная
def variable():
    if not (name()): error("Некорректный идентификатор")
    scan()
    if nxtsymb == '[':
        scan()
        expression()
        if nxtsymb != ']': error()
        scan()


# арифметическая операция
def arithmetic_operation():
    return nxtsymb in ['%', '*', '**', '+', '-', '..', '/']



# оператор присваивания
def assignment_operator():
    scan()
    variable()
    if nxtsymb != '=': error("Не встречено '='")
    scan()
    expression()


# условный оператор
def conditional_operator():
    if nxtsymb != 'IF': error("Не встречено IF")
    scan()
    if nxtsymb != '(': error("Ожидалось '('")
    condition()
    if nxtsymb != ')': error("Не встречено ')'")
    scan()
    # compound
    if nxtsymb == 'else':
        scan()
        # compound compound_operator()


# условие
def condition():
    if unary_log_operation():
        scan()
        if nxtsymb != '(': error("Ожидалось '('")
        log_expression()
        if nxtsymb != ')': error("Не встречено ')'")
        scan()
    else:
        log_expression()
        while binary_log_operation():
            log_expression()


# унарная логическая операция
def unary_log_operation():
    return nxtsymb == 'not'


# логическое выражение
def log_expression():
    scan()
    expression()
    comparison_operation()
    scan()
    expression()


# операция сравнения
def comparison_operation():
    return nxtsymb in ['!=', '<', '<=', '==', '>', '>=']


# бинарная логическая операция
def binary_log_operation():
    return nxtsymb == 'and' or nxtsymb == 'or'


# цикл while
def while_loop():
    if nxtsymb != 'while': error()
    scan()
    if nxtsymb != '(': error()
    condition()
    if nxtsymb != ')': error()
    scan()
    # compound_operator()


# цикл do while
def do_while_loop():
    if nxtsymb != 'do': error()
    scan()
    #compound_operator()
    if nxtsymb != 'while': error()
    scan()
    if nxtsymb != '(': error()
    scan()
    condition()
    if nxtsymb != ')': error()


# цикл for
def for_loop():
    if nxtsymb != 'for': error()
    scan()
    if nxtsymb != '(': error()
    assignment_operator()
    if nxtsymb != ';': error()
    condition()
    if nxtsymb != ';': error()
    assignment_operator()
    if nxtsymb != ')': error()
    scan()
    compound_operator()


# оператор goto
def goto_statement():
    if nxtsymb != 'goto': error()
    scan()
    if not (name()): error()
    scan()


# оператор continue
def continue_operator():
    return nxtsymb == 'continue'


# оператор return
def return_operator():
    if nxtsymb != 'return': error()
    scan()
    expression()


# оператор print
def print_operator():
    if nxtsymb != 'print': error()
    scan()
    expression()


program()
