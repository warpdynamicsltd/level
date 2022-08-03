import level.core.ast as ast

class ParseException(Exception):
    pass

class Terminal:
    pass

class Func:
    pass

class Symb:
    hide_var_values = False

    def __init__(self, name, value, meta=None):
        self.name = name
        self.meta = meta
        self.value = value
        self.args = []

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return type(self) is type(other) and self.name == other.name

    def __repr__(self):
        if not Symb.hide_var_values:
            return f'[{self.name}]({"".join(map(str, self.value))})'
        else:
            return f'[{self.name}]'

    def __str__(self):
        if not Symb.hide_var_values:
            return f'[{self.name}]({"".join(map(str, self.value))})'
        else:
            return f'[{self.name}]'


class Root(Symb):
    def __init__(self, value, meta=None):
        Symb.__init__(self, 'root', value, meta)

    def __str__(self):
        return "".join(map(str, self.value))

    def __repr__(self):
        return str(self)

class StringSymb(Symb, Terminal):
    def __str__(self):
        return f"S({self.value})"

    def __repr__(self):
        return str(self)

class TokenSymb(Symb, Terminal):
    def __init__(self, value, meta=None):
        Symb.__init__(self, 'T', value, meta)

class BracketSymb(Symb):
    def __init__(self, name, opening, closing, value):
        self.opening = opening
        self.closing = closing
        Symb.__init__(self, name=f'{name}_bracket{self.opening}{self.closing}', value=value)

class ArgSymb(Symb):
    pass

class NarySymb(Symb, Func):
    pass

class BinarySymb(Symb, Func):
    pass

class Parser:
    def __init__(self, s):
        self.raw = s
        self.open_brackets = ['{', '[', '(']
        self.close_brackets = ['}', ']', ')']
        self.nary_symbols = [';', ',']
        self.operator_symbols = set(['=', '+', '-', '*', '&', '^', '|', '\\', '/', '$', '.', '!'])
        self.binary_symbols = [['='], ['=='], ['and', 'or', 'xor'],
                               ['+', '-'],
                               ['*', '/', '%'],
                               ['.', ':']]
        self.unary_symbols = ['not', '+', '-']
        self.string_markers = ['"', "'"]

        self.string_escape_map = {
            'n': chr(0xa),
            'r': chr(0xd),
            't': chr(0x9),
            '"': '"',
            "'": "'",
            "\\": "\\"
        }

        self.root = Root(list(s))

        self.function_names = set()

    def parse(self):
        self.symbolise_strings()
        self.tokenize(self.is_token_char)
        self.symbolise_brackets()
        for c in self.nary_symbols:
            self.symbolise_nary(c)
        self.symbolise_binary(['='])
        self.symbolise_binary(['+', '-'])
        self.symbolise_binary(['*'])

        return self.parse_program()

    def transform_string(self, s):
        res = []
        escape_mode = False
        hex_mode = False
        hex_value = str()
        for i, c in enumerate(s):
            if hex_mode:
                if len(hex_value) < 2:
                    hex_value += c
                    continue
                else:
                    res.append(chr(int(hex_value, base=16)))
                    hex_mode = False
                    escape_mode = False
                    continue


            if escape_mode:
                if c in self.string_escape_map:
                    res.append(self.string_escape_map[c])
                if c == 'x':
                    hex_mode = True
                    continue
                else:
                    escape_mode = False
                continue

            if c == '\\':
                escape_mode = True
                continue

            else:
                if c != '\\':
                    res.append(c)

        return "".join(res)


    def symbolise_strings(self):
        string_mode = False
        last_marker = None
        start_index = 0
        s = str()
        _id = 0
        shift = 0
        current = self.root.value
        for i, c in enumerate(self.root.value):
            j = i + shift
            if not string_mode and c in self.string_markers:
                last_marker = c
                string_mode = True
                start_index = j
                s = str()
                continue

            if string_mode:
                if self.root.value[i - 1] != '\\' and c == last_marker:
                    string_mode = False
                    last_marker = None
                    symb = StringSymb(f's{_id}', self.transform_string(s))
                    _id += 1
                    current = current[:start_index] + [symb] + current[j + 1:]
                    shift -= (j - start_index)
                else:
                    s += c


        self.root.value = current

    def is_token_char(self, c):
        return c.isalnum() or c == '_'

    def is_operator_char(self, c):
        return c in self.operator_symbols

    def tokenize(self, is_token_char):
        current = []
        token_mode = False
        token = str()
        space_mode = False
        spaces = []

        for i, c in enumerate(self.root.value):
            if issubclass(type(c), Symb):
                current.append(c)
                continue

            if space_mode:
                if c.isspace():
                    spaces.append(c)
                else:
                    space_mode = False

            if token_mode:
                if is_token_char(c):
                    token += c
                    continue
                else:
                    token_mode = False
                    current.append(TokenSymb(token))
                    token = str()

            if is_token_char(c):
                token_mode = True
                token += c
                continue

            if c.isspace():
                space_mode = True
                continue

            current.append(c)

        if len(token) > 0:
            current.append(TokenSymb(token))

        self.root.value = current


    def symbolise_brackets(self):
        stack = []
        current = list(self.root.value)
        shift = 0
        name = 0
        for i, c in enumerate(self.root.value):
            i = i + shift
            for oid, ob in enumerate(self.open_brackets):
                if ob == c:
                    stack.append((i, oid))

            for cid, cb in enumerate(self.close_brackets):
                if cb == c:
                    j, oid = stack.pop()
                    if oid != cid:
                        raise Exception('wrong closing bracket')

                    symb = BracketSymb(name, self.open_brackets[oid], self.close_brackets[oid], current[j + 1: i])
                    name += 1
                    # symb.value = current[j + 1: i]
                    current = current[:j] + [symb] + current[i + 1:]
                    shift -= (i - j)

        self.root.value = current


    def symbolise_nary_s(self, s, sep):
        args = []
        arg = ArgSymb('arg', [])
        for c in s:
            if c == sep:
                if len(arg.value) > 0:
                    args.append(arg)
                arg = ArgSymb('arg', [])
                continue

            arg.value.append(c)

        if args and len(arg.value) > 0:
            args.append(arg)

        res = None
        if args:
            symb = NarySymb(name=sep, value=args)
            res = symb

        return res

    def operator(self, op, a, b):
        arg1 = ArgSymb('arg', a)
        res = BinarySymb("op", b)

    def symbolise_binary_s(self, s, ops):
        args = []
        arg = ArgSymb('arg', [])
        operators = []
        for c in s:
            if c in ops:
                if len(arg.value) > 0:
                    args.append(arg)
                    operators.append(c)
                arg = ArgSymb('arg', [])
                continue

            arg.value.append(c)

        if args and len(arg.value) > 0:
            args.append(arg)
        else:
            return None

        if len(args) < 2:
            raise ParseException("Not enough arguments for operator")

        res = BinarySymb(operators.pop(0), [args[0], args[1]])
        for arg in args[2:]:
            res = BinarySymb(operators.pop(0), [ArgSymb('arg', [res]), arg])

        return res

    def expand(self, node, fun):
        t = type(node)
        if not issubclass(t, Symb):
            return

        if issubclass(t, Terminal):
            return

        for v in node.value:
            self.expand(v, fun)

        res = fun(node.value)
        if res is not None:
            node.value = [res]


    def symbolise_nary(self, sep):
        def symbolise(s):
            return self.symbolise_nary_s(s, sep)

        self.expand(self.root, symbolise)
        return self

    def symbolise_binary(self, ops):
        def symbolise(s):
            return self.symbolise_binary_s(s, ops)

        self.expand(self.root, symbolise)
        return self

    """
    Draft Program build POC
    """

    def parse_program(self):
        s = iter(self.root.value)
        elem = next(s)
        defs = []
        while(type(elem) == TokenSymb and elem.value == 'def'):
            fun_def = self.parse_func_def(s)
            defs.append(fun_def)
            elem = next(s)

        # print(fun_def)
        if not(type(elem) == TokenSymb and elem.value == 'program'):
            raise ParseException('expected: program')

        elem = next(s)

        statement_list = self.parse_statement_list(elem)

        return ast.Program(def_block=ast.DefBlock(*defs), code_block=statement_list)

    def parse_func_def(self, s):
            elem = next(s)
            if not(type(elem) is TokenSymb):
                raise ParseException('expected: function name')

            fun_name = elem.value
            self.function_names.add(fun_name)

            elem = next(s)
            if not(type(elem) is BracketSymb) and elem.opening == '(':
                raise ParseException('expected: (')

            elem_list = self.parse_list(elem, ',')
            var_list = ast.VarList(*[ast.Var(v[0].value) for v in elem_list])
            elem = next(s)

            if not (type(elem) is BracketSymb and elem.opening == '{'):
                raise ParseException('expected: {')

            statement_list = self.parse_statement_list(elem)

            res = ast.SubroutineDef(fun_name, var_list, statement_list)
            # print(res)

            return res

    def parse_list(self, node, sep):
        s = iter(node.value)
        elem = next(s)

        res = None

        if type(elem) is TokenSymb:
            res = [[elem]]

        if type(elem) is BracketSymb:
            res = [[elem]]

        if type(elem) is NarySymb and elem.name == sep:
            res = []
            for e in elem.value:
                res.append(e.value)

        if res is None:
            raise ParseException('expected: comma separated list or one argument')

        return res

    def parse_statement_list(self, elem):
        statement_list = self.parse_list(elem, ';')
        # print(statement_list)

        statements = []
        for statement in statement_list:
            statement = self.parse_statement(statement)
            statements.append(statement)

        return ast.StatementList(*statements)


    def parse_statement(self, statement):
        # print(statement)
        if type(statement) is list and \
                type(statement[0]) is TokenSymb and \
                statement[0].value == 'init'and \
                type(statement[1]) is TokenSymb:
            return ast.Init(ast.Var(statement[1].value))

        if type(statement) is list and type(statement[0]) is BinarySymb and statement[0].name == '=':
            elem = statement[0].value[0].value[0]
            if type(elem) is TokenSymb:
                var_name = elem.value
                return ast.Assign(ast.Var(var_name), self.parse_expression(statement[0].value[1].value))

        if type(statement) is list and type(statement[0]) is TokenSymb:
            if statement[0].value == 'echo':
                expression = self.parse_expression(statement[1:])
                res = ast.Echo(expression)
                return res
            if statement[0].value == 'return':
                expression = self.parse_expression(statement[1:])
                res = ast.Return(expression)
                return res


            if type(statement) is list  and \
                    len(statement) > 2 and \
                    type(statement[0]) is TokenSymb and \
                    type(statement[1]) is BracketSymb and \
                    type(statement[2]) is BracketSymb:

                condition = self.parse_expression([statement[1]])
                statement_list1 = self.parse_statement_list(statement[2])
                # print(statement[3], statement[4])
                if len(statement) > 4 and type(statement[3]) is TokenSymb and type(statement[4]) is BracketSymb:
                    statement_list2 = self.parse_statement_list(statement[4])
                    if statement[0].value == 'if' and statement[3].value == 'else':
                        return ast.IfElse(condition, statement_list1, statement_list2)
                else:
                    if statement[0].value == 'if':
                        return ast.IfElse(condition, statement_list1, ast.StatementList())


        raise ParseException('unexpected statement')

    # def parse_expression(self, exp):
    #     # print('expression: ', exp)
    #     if type(exp) is TokenSymb:
    #         if exp.value.isdigit():
    #             return ast.Const(int(exp.value))
    #         else:
    #             return ast.Var(exp.value)

    def parse_expression(self, segment):
        # print ("SEGMENT >> ", segment)
        if len(segment) == 1:
            exp = segment[0]
            if type(exp) is TokenSymb:
                if exp.value.isdigit():
                    return ast.Const(int(exp.value))
                else:
                    return ast.Var(exp.value)

            if type(exp) is BracketSymb:
                # print(exp.value)
                return self.parse_expression(exp.value)

            if type(exp) is BinarySymb:
                # print(exp)
                # print("ARGS >> ", exp.value[0].value, exp.value[1].value)
                exp1 = self.parse_expression(exp.value[0].value)
                exp2 = self.parse_expression(exp.value[1].value)
                # print(type(exp1), type(exp2))
                if exp.name == '+':
                    return ast.Add(exp1, exp2)
                if exp.name == '*':
                    return ast.Mul(exp1, exp2)
                if exp.name == '-':
                    #print(exp)
                    return ast.Sub(exp1, exp2)

        if len(segment) == 2 and type(segment[1]) is BracketSymb:
            fun_name = segment[0].value
            # print(type(fun_name))
            # print(self.function_names)
            if fun_name in self.function_names:
                expression_list = self.parse_list(segment[1], ',')
                # print(expression_list)
                expressions = [self.parse_expression(e) for e in expression_list]
                return ast.SubroutineCall(fun_name, *expressions)
        # print ("ERROR SEGMENT >> ", segment)
        raise ParseException('unexpected expression')