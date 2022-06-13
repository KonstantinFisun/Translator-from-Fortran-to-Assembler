import lab1
import json
import re

# Классы токенов
CLASSES_OF_TOKENS = ['W', 'I', 'O', 'R', 'N', 'C']


def is_identifier(token):
    return re.match(r'^I\d+$', inverse_tokens[token]) or \
           token in ['PRINT']

# Расставим приоритет
def get_priority(token):
    if token in ['(', 'DO', 'IF', '[', 'АЭМ', 'Ф']:
        return 0
    if token in [')', ',', 'ELSE', 'THEN', ']']:
        return 1
    if token == '::' or token == 'GOTO':
        return 2
    if token == 'or':
        return 3
    if token == 'and':
        return 4
    if token == 'not':
        return 5
    if token in ['<', '<=', '<>', '=', '>', '>=']:
        return 6
    if token == '+' or token == '-':
        return 7
    if token in ['*', '/', '**', '%']:
        return 8
    if token in ['END', 'SUBROUTINE', 'PROGRAM']:
        return 9
    return -1

# лексемы (код-значение)
tokens = {}

# файлы, содержащие все таблицы лексем
for token_class in CLASSES_OF_TOKENS:
    with open('%s.json' % token_class, 'r') as read_file:
        data = json.load(read_file)
        tokens.update(data)

# лексемы (значение-код)
inverse_tokens = {val: key for key, val in tokens.items()}

# файл, содержащий последовательность кодов лексем входной программы
f = open('tokens.txt', 'r')
inp_seq = f.read() # Входящая последовательность
f.close()

# Регулярка: [W|I|O|R|N|C]\\d+
regexp = '[' + '|'.join(CLASSES_OF_TOKENS) + ']' + '\d+'
# Считали все лексемы из файла
match = re.findall(regexp, inp_seq)

# Получили имена лексем
t = [tokens[i] for i in match]


i = 0 # итерация
stack = [] # Стек
# Выходная последовательность содержащая польскую запись
out_seq = '' # Выходная последовательность
# количество массивов, проц уровень
aem_count = proc_level = 1
# Счетчики выражений
func_count = tag_count = proc_num = if_count = while_count = repeat_count = \
             for_count = begin_count = end_count = 0
is_func = False

while i < len(t):
    # Получаем приоритет текущей лексемы
    p = get_priority(t[i]) # Получаем приоритет

    # Конец процедуры
    if t[i]+' '+t[i+1] == 'END PROGRAM':
        stack.pop()
        out_seq += 'КП ' + t[i+1]
        break

    # Если нет в приоритете
    elif p == -1:
        # Если не переход на новую строчку добавляем слово и пробел
        if t[i] != '\n':
            out_seq += t[i] + ' '

        # Если это функция и следующий элемент (
        if is_func and t[i + 1] == '(':
            i += 2 # Прибавляем к текущему шагу
            block = [] # Создаем пустой блок
            while t[i] != ')': # Выполняем пока не закончились
                block.append(t[i]) # Добавляем в блок
                i += 1 # Переходим к следующему
            i -= 1
            is_func = False
    else:
        # Если встретили индекс массива
        if t[i] == '[':
            aem_count += 1 # Добавляем к счетчику
            stack.append(str(aem_count) + ' АЭМ') # Добавляем в наш стек
        # Если индекс закончился
        elif t[i] == ']':
            # Пока
            while not(re.match(r'^\d+ АЭМ$', stack[-1])):
                out_seq += stack.pop() + ' ' # Выходная последовательность
            out_seq += stack.pop() + ' '
            aem_count = 1

        # Если встретили скобку
        elif t[i] == '(':
            if is_identifier(t[i - 1]):
                func_count += 1
                stack.append(str(func_count) + ' Ф')
            else:
                stack.append(t[i])
        # Если закончилось выражение
        elif t[i] == ')':
            if t[i + 1] == ':':
                i += 2
                out_seq += '1 ' + t[i] + ' КО '
            else:
                while stack[-1] != '(' and not(re.match(r'^\d+ Ф$', stack[-1])):
                    out_seq += stack.pop() + ' '
                if re.match(r'^\d+ Ф$', stack[-1]):
                    stack.append(str(func_count + 1) + ' Ф')
                    func_count = 0
            stack.pop()
        # Если встретили запятую
        elif t[i] == ',':
            # Если встретили не функцию и не массив
            while not(re.match(r'^\d+ АЭМ$', stack[-1])) and not(re.match(r'^\d+ Ф$', stack[-1])) :
                out_seq += stack.pop() + ' '
            # Если встретили массив
            if re.match(r'^\d+ АЭМ$', stack[-1]):
                aem_count += 1
                stack.append(str(aem_count) + ' АЭМ')
            # Если встретили функцию
            if re.match(r'^\d+ Ф$', stack[-1]):
                func_count += 1
                stack.append(str(func_count) + ' Ф')
            # Достали из стека
            stack.pop()

        # Если операция GOTO
        # БП - безусловный переход
        elif t[i] == 'GOTO':
            out_seq += t[i + 1] + ' БП '
            i += 2
        # Если встретили IF
        elif t[i] == 'IF':
            stack.append(t[i])
            if_count += 1
        # Если встретили THEN
        elif t[i] == 'THEN':
            # Идем пока в топе не встетим IF
            while stack[-1] != 'IF':
                out_seq += stack.pop() + ' '
            # Номер метки
            tag_count += 1
            # Добавляем в верхний элемент стек
            stack[-1] += ' М' + str(tag_count)
            # Выходную последовательность
            out_seq += 'М' + str(tag_count) + ' УПЛ '
        elif t[i] == 'ELSE':
            # Пока не совпадет верхний элемент
            while not(re.match(r'^IF М\d+$', stack[-1])):
                out_seq += stack.pop() + ' ' # Добавляем
            # Достаем из стека
            stack.pop()
            # Номер метки
            tag_count += 1
            # Добавляем в стек
            stack.append('IF М' + str(tag_count))
            # Выходная
            out_seq += 'М' + str(tag_count) + ' БП М' + str(tag_count - 1) + ' : '

        # Если встретили DO WHILE
        elif t[i]+' '+t[i+1] == 'DO WHILE':
            tag_count += 1
            stack.append('DO WHILE М' + str(tag_count))
            out_seq += 'М' + str(tag_count) + ' : '
            while_count += 1
            i+=1

        # Если встретили функцию
        elif t[i] in ['SUBROUTINE']:
            if t[i] == 'SUBROUTINE':
                is_func = True
            proc_num += 1
            stack.append('PROC ' + str(proc_num) + ' ' + str(proc_level))

        # Если встретили END
        elif t[i]+''+t[i+1] == 'END DO':
            end_count += 1
            proc_level = begin_count - end_count + 1
            while stack[-1] != 'DO WHILE':
                out_seq += stack.pop() + ' '
            stack.pop()

            if not(if_count > 0 and re.match(r'^IF М\d+$', stack[-1])) and not(while_count > 0 and re.match(r'^DO WHILE М\d+ М\d+$', stack[-1])):
                stack.append(t[i])

        # Надо разобраться
        elif t[i] == '/n':

            if len(stack) > 0 and re.match(r'^PROC', stack[-1]):
                num = re.findall(r'\d+', stack[-1])
                stack.pop()
                out_seq += str(num[0]) + ' ' + str(num[1]) + ' НП '

            elif len(stack) > 0 and stack[-1] == 'END':
                stack.pop()
                out_seq += 'КП '

            elif if_count > 0 or while_count > 0:
                while not(len(stack) > 0 and stack[-1] == 'BEGIN') and \
                      not(if_count > 0 and re.match(r'^IF М\d+$', stack[-1])) and \
                      not(while_count > 0 and re.match(r'^DO WHILE М\d+ М\d+$', stack[-1])):
                    out_seq += stack.pop() + ' '

                if if_count > 0 and re.match(r'^IF М\d+$', stack[-1]):
                    tag = re.search('М\d+', stack[-1]).group(0)
                    out_seq += tag + ' : '
                    if_count -= 1

                if while_count > 0 and re.match(r'^DO WHILE М\d+ М\d+$', stack[-1]):
                    tag = re.findall('М\d+', stack[-1])
                    out_seq += tag[0] + ' БП ' + tag[1] + ' : '
                    while_count -= 1

                if len(stack) > 0 and stack[-1] != 'DO':
                    stack.pop()
            else:
                while len(stack) > 0 and stack[-1] != 'DO':
                    out_seq += stack.pop() + ' '
        else:
            while len(stack) > 0 and get_priority(stack[-1]) >= p:
                out_seq += stack.pop() + ' '
            stack.append(t[i])
    i += 1

while len(stack) > 0:
    out_seq += stack.pop() + ' '

# файл, содержащий обратную польскую запись
f = open('reverse_polish_entry.txt', 'w')
f.write(out_seq)
f.close()
