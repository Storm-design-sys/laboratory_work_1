
tokens = []
pos = 0

# Лексер
def tokenosize(s):

    slovar = {
        "+": "PLUS",
        "-": "MINUS",
        "*": "YMNOZH",
        "/": "DELIT",
        "&": "BIT",
        "(": "LPAREN",
        ")": "RPAREN",
        ",": "COMMA"
    }

    sp = []
    
    i = 0
    err = False

    while i < len(s):
        c = s[i]

        if c == " ":
            i += 1
            continue

        if c in "+-*/&(),":
            sp.append((slovar[c], c))
            i += 1
            continue

        if c.isdigit() or c == ".":
            num = ""
            while i < len(s) and (s[i].isdigit() or s[i] == "."):
                num += s[i]
                i += 1
            sp.append(("NUMBER", num))
            continue

        if c.isalpha():
            word = ""
            while i < len(s) and (s[i].isalpha()):
                word += s[i]
                i += 1
            if word == "round":
                sp.append(("IDENT", "round"))
            else:
                err = True
                break
            continue
    
    sp.append(("END", None))

    return sp, err

def peek():
    return tokens[pos]

def advance():
    global pos
    x = tokens[pos]
    pos += 1
    return x

def expect(type_):
    if peek()[0] == type_:
        return advance()
    else:
        raise ValueError(f"Ожидался {type_}, а получен {peek()}")


# Парсер для чисел, скобок, вызовов функций
def parse_primary():
    
    if peek()[0] == "NUMBER":
        return float(advance()[1])

    elif peek()[0] == "LPAREN":
        advance()
        inner = parse_expr()
        expect("RPAREN")
        return inner
    elif peek()[0] == "IDENT":
        return parse_function()
    else:
        raise ValueError("Неожиданный токен")

# Парсер для унарных + и -
def parse_unary():
    if peek()[0] == 'MINUS':
        advance()
        operand = parse_unary()
        return ("u-", operand)
    
    elif peek()[0] == "PLUS":
        advance()
        return parse_unary()

    else:
        return parse_primary()
    
# Парсер для умножения и деления
def parse_mul():
    left = parse_unary()
    while (peek()[0] == "YMNOZH") or (peek()[0] == "DELIT"):
        op = advance()[1]
        right = parse_unary()
        left = (op, left, right)
    return left

# Парсер для сложения и вычитания
def parse_add():
    left = parse_mul()
    while (peek()[0] == "PLUS") or (peek()[0] == "MINUS"):
        op = advance()[1]
        right = parse_mul()
        left = (op, left, right)
    return left

# Парсер с & 
def parse_expr():
    left = parse_add()
    while peek()[0] == "BIT":
        op = advance()[1]
        right = parse_add()
        left = (op, left, right)
    return left

# Парсер round()
def parse_function():
    per = advance()
    expect("LPAREN")
    args = [parse_expr()]
    while peek()[0] == "COMMA":
        advance()
        args.append(parse_expr())
    expect("RPAREN")

    if per[1] == "round":
        if len(args) == 2:
            return ("round", args[0], args[1])
        else:
            raise ValueError("Надо передать два аргумента")
    else:
        raise ValueError("Неизвестная функция")

# Дерево
def calc(node):
    if type(node) != tuple:
        return node
    
    if node[0] == "u-":
        return -calc(node[1])
    elif node[0] == "+":
        return calc(node[1]) + calc(node[2])
    elif node[0] == "-":
        return calc(node[1]) - calc(node[2])
    elif node[0] == "*":
        return calc(node[1]) * calc(node[2])
    elif node[0] == "/":
        return calc(node[1]) / calc(node[2])
    elif node[0] == "round":
        return round(calc(node[1]), int(calc(node[2])))
    elif node[0] == "&":
        a = calc(node[1])
        b = calc(node[2])
        if a.is_integer() and b.is_integer():
            return float(int(a) & int(b))
        else:
            raise ValueError("& работает только с целыми числами!")

# Все вместе
def run(expr):
    global tokens, pos
    pos = 0

    tokens, err = tokenosize(expr)
    if err:
        raise ValueError("Ошибка лексера")

    tree = parse_expr()
    
    if peek()[0] == "END":
        return calc(tree)
    else:
        raise ValueError("Лишние токены")


expr = input("Введите выражение: ")
print("Результат:", run(expr))

