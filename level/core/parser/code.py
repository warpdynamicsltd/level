import struct
import re

from level.mathtools.float import  float80

import level.core.parser.builtin as builtin
import level.core.ast as ast
import level.core.parser.linker

class ParseException(Exception):
    def __init__(self, message=""):
        message = f"parser error: {message}"
        Exception.__init__(self, message)

class MetaParserInfo:
    def __init__(self, n_line, n_char, lead=None):
        self.n_line = n_line
        self.n_char = n_char
        self.lead = lead

    def __str__(self):
        if self.lead is not None:
            lead = self.lead.key
        else:
            lead = "main"
        return f"{lead} : line {self.n_line}[{self.n_char}]"

    def __repr__(self):
        return str(self)

class Char:
    def __init__(self, c, meta=None):
        self.c = c
        self.meta = meta

    def __eq__(self, other):
        if type(other) is Char:
            return self.c == other.c

        if type(other) is str:
            return self.c == other

        raise ParseException('unexpected type')

    def __ne__(self, other):
        return not self.__eq__(other)

    def __radd__(self, other):
        return other + self.c


    def __hash__(self):
        return hash(self.c)

    def __str__(self):
        return self.c

    def __repr__(self):
        return str(self)

class Symb:
    def __init__(self, name, value, meta=None):
        """

        Parameters
        ----------
        name - name of type of symbol, often its graphical representation
        value - list of parsed characters of alphabet and symbols, if substituted recursively for all symbols returns the original text
        meta - meta value related to symbol (e.g. original line numer and position (line_n, char_n))
        """
        self.name = name
        self.value = value
        self.meta = meta

    def __str__(self):
        return f'[{self.name}]({"".join(map(str, self.value))})'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return False

def meta(s, i=0):
    if isinstance(s, Symb) or isinstance(s, Char):
        return s.meta
    if type(s) is list and s:
        return s[i].meta

    return None


class StringSymb(Symb):
    def __init__(self, value, meta=None):
        Symb.__init__(self, 'S', value, meta)

    def string(self):
        res = str()
        for c in self.value:
            res += c

        return res

class TerminalSymb(Symb):
    def __init__(self, value, meta=None):
        Symb.__init__(self, 'T', value, meta)

    def __eq__(self, other):
        if issubclass(type(other), TerminalSymb):
            return self.value == other.value

        if type(other) is str:
            return "".join(map(str, self.value)) == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def visual(self):
        return "".join(map(str, self.value))

    def __hash__(self):
        return hash(self.visual())

# class TerminalVarSymb(TerminalSymb):
#     def __init__(self, value, meta=None):
#         TerminalSymb.__init__(self, 'T', value, meta)
#
# class TerminalOpSymb(TerminalSymb):
#     def __init__(self, value, meta=None):
#         TerminalSymb.__init__(self, 'T', value, meta)

class BracketSymb(Symb):
    def __init__(self, opening, closing, value, meta=None):
        self.opening = opening
        self.closing = closing
        Symb.__init__(self, name=f'{self.opening}|{self.closing}', value=value, meta=meta)

    def __eq__(self, other):
        return type(other) is BracketSymb and self.opening == other.opening and self.closing == other.closing


class FuncSymb(Symb):
    def __init__(self, op, value, meta, *args):
        self.op = op
        self.args = args
        Symb.__init__(self, name=op, value=value, meta=meta)

    def __str__(self):
        return f"[{self.op}]({','.join(map(str, self.args))})"

class BinaryFuncSymbol(FuncSymb):
    def __init__(self, op, arg1, arg2, meta=None):
        value = [arg1, op, arg2]
        FuncSymb.__init__(self, op, value, meta, arg1, arg2)


class ArgSymb(Symb):
    def __init__(self, value, meta=None):
        Symb.__init__(self, name='A', value=value, meta=meta)
        self.arg = value[0]


class Root(Symb):
    def __init__(self, value):
        Symb.__init__(self, 'Root', value)


class Parser:
    def __init__(self, text):
        self.text = text
        linker = level.core.parser.linker.Linker()
        linker.text_recursive(text, lead=None)
        #self.root = Root(self.text_to_alphabet_characters(text))
        self.root = Root(linker.chars)

        self.string_markers = ['"', "'"]
        self.string_escape_map = {
            'n': chr(0xa),
            'r': chr(0xd),
            't': chr(0x9),
            '"': '"',
            "'": "'",
            "\\": "\\"
        }

        self.operator_chars = set(['-', '+', '=', '*', '&', '^', '|', '\\', '/', '$', '.', '!', '<', '>', '%'])

        self.binary_operators = builtin.binary_operators

        self.composed_operators = {'<-', '==', '!=', '<=', '>=', '$='}

        self.unary_operators = builtin.unary_operators

        self.open_brackets = ['{', '[', '(', 'begin']
        self.close_brackets = ['}', ']', ')', 'end']


    def parse(self):
        self.symbolise_strings()
        self.comment()
        # self.tokenize(self.is_operator_char, TerminalSymb)
        self.tokenize_wanted(self.is_operator_char, TerminalSymb, self.is_long_operator)
        self.tokenize_single(self.is_operator_char, TerminalSymb)
        self.tokenize(self.is_token_char, TerminalSymb)
        self.remove_spaces()
        self.symbolise_brackets()
        return self.parse_program(self.root.value)


    def text_to_alphabet_characters(self, text):
        line_n = 1
        char_n = 1
        res = []
        for c in text:
            res.append(Char(c, meta=MetaParserInfo(line_n, char_n)))

            char_n += 1

            if c == '\n':
                line_n += 1
                char_n = 1

        return res

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
                    res.append(Char(chr(int(hex_value, base=16)), meta=c.meta))
                    hex_mode = False
                    escape_mode = False
                    continue


            if escape_mode:
                if c in self.string_escape_map:
                    res.append(Char(self.string_escape_map[c], meta=c.meta))
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

        return res

    def symbolise_strings(self):
        string_mode = False
        last_marker = None
        start_index = 0
        s = []
        _id = 0
        shift = 0
        current = self.root.value
        n_slashes = 0
        for i, c in enumerate(self.root.value):
            j = i + shift
            if not string_mode and c in self.string_markers:
                last_marker = c
                string_mode = True
                start_index = j
                s = []
                continue

            if string_mode:
                if (n_slashes % 2 == 0) and c == last_marker:
                    string_mode = False
                    last_marker = None
                    tr_s = self.transform_string(s)
                    symb = StringSymb(tr_s, meta=tr_s[0].meta)
                    _id += 1
                    current = current[:start_index] + [symb] + current[j + 1:]
                    shift -= (j - start_index)
                else:
                    s.append(c)

            if c == '\\':
                n_slashes += 1
            else:
                n_slashes = 0


        self.root.value = current

    def comment(self):
        current = []
        comment_mode = False
        for i, c in enumerate(self.root.value):
            if c == '#':
                comment_mode = True

            if c == '\n':
                comment_mode = False

            if not comment_mode:
                current.append(c)

        self.root.value = current


    def is_token_char(self, c):
        return c.c.isalnum() or c == '_' or c == ':'

    def is_num_char(self, c):
        return c.c.isdigit()

    def is_operator_char(self, c):
        return c in self.operator_chars

    def tokenize_single(self, is_token_char, T):
        current = []
        for i, c in enumerate(self.root.value):
            if type(c) is Char and is_token_char(c):
                current.append(T([c], meta=c.meta))
            else:
                current.append(c)

        self.root.value = current

    def is_long_operator(self, s):
        return s in self.composed_operators

    def tokenize(self, is_token_char, T, f=lambda x: True):
        current = []
        token_mode = False
        token = []
        space_mode = False
        spaces = []

        def append_token(current, token):
            temp = T(token, meta=token[0].meta)
            if f(temp.visual()):
                current.append(temp)
            else:
                current += token

        for i, c in enumerate(self.root.value):
            if space_mode:
                if type(c) is Char and c.c.isspace():
                    spaces.append(c)
                else:
                    space_mode = False

            if token_mode:
                if type(c) is Char and is_token_char(c):
                    token.append(c)
                    continue
                else:
                    token_mode = False
                    append_token(current, token)
                    token = []

            if type(c) is Char and is_token_char(c):
                token_mode = True
                token.append(c)
                continue

            if type(c) is Char and c.c.isspace():
                space_mode = True

            current.append(c)

        if len(token) > 0:
            append_token(current, token)

        self.root.value = current

    def tokenize_wanted(self, is_token_char, T, f=lambda x: True):
        current = []
        token_mode = False
        token = []
        space_mode = False
        spaces = []

        def wanted(token):
            if token:
                temp = T(token, meta=token[0].meta)
                return f(temp.visual())

            return False

        def append_token(current, token):
            temp = T(token, meta=token[0].meta)
            if f(temp.visual()):
                #print(temp)
                current.append(temp)
            else:
                current += token

        for i, c in enumerate(self.root.value):
            if space_mode:
                if type(c) is Char and c.c.isspace():
                    spaces.append(c)
                else:
                    space_mode = False

            if wanted(token):
                append_token(current, token)
                token = []
                token_mode = False

            if token_mode:
                if type(c) is Char and is_token_char(c):
                    token.append(c)
                    continue
                else:
                    token_mode = False
                    append_token(current, token)
                    token = []

            if type(c) is Char and is_token_char(c):
                token_mode = True
                token.append(c)
                continue

            if type(c) is Char and c.c.isspace():
                space_mode = True

            current.append(c)

        if len(token) > 0:
            append_token(current, token)

        self.root.value = current

    def remove_spaces(self):
        current = []
        for c in self.root.value:
            if type(c) is Char and c.c.isspace():
                continue

            current.append(c)

        self.root.value = current

    def symbolise_brackets(self):
        stack = []
        current = list(self.root.value)
        shift = 0
        for i, c in enumerate(self.root.value):
            i = i + shift
            for oid, ob in enumerate(self.open_brackets):
                if ob == c:
                    stack.append((i, oid, c))

            for cid, cb in enumerate(self.close_brackets):
                if cb == c:
                    j, oid, b = stack.pop()
                    if oid != cid:
                        raise ParseException(f"wrong closing bracket '{c}' in {c.meta}")

                    content = current[j + 1: i]
                    symb = BracketSymb(self.open_brackets[oid], self.close_brackets[oid], content, meta=b.meta)
                    current = current[:j] + [symb] + current[i + 1:]
                    shift -= (i - j)

        if stack:
            _, _, c = stack.pop()
            raise ParseException(f"no closure for '{c}' in {c.meta}")

        self.root.value = current


    def parse_list(self, stream, delimiter):
        arg_value = []
        args = []
        for c in stream:
            if c == delimiter:
                if arg_value:
                    args.append(ArgSymb(value=arg_value, meta=arg_value[0].meta))
                    arg_value = []
                    continue
                else:
                    raise ParseException(f"expected any expression in {c.meta}")

            arg_value.append(c)

        if arg_value:
            args.append(ArgSymb(value=arg_value, meta=arg_value[0].meta))

        return args

    def try_parse(self, parse_fun, *args):
        try:
            return parse_fun(*args)
        except ParseException as e:
            return None

    def parse_unary(self, stream, op):
        if not (type(stream) is list and stream):
            ParseException()

        if stream[0] != op:
            raise ParseException(f"expected unary expression '{op}' in {stream[0].meta}")

        exp = self.parse_expression(stream[1:])
        exp.meta = stream[0].meta
        return self.unary_operators[op](exp).add_raw_str(op)

    def try_parse_unary(self, stream, op):
        try:
            return self.parse_unary(stream, op)
        except ParseException as e:
            return None

    def pre_parse_binary(self, stream, ops):
        if not(type(stream) is list and stream):
            raise ParseException()

        k = None
        op = None
        for i, c in enumerate(reversed(stream)):
            if c in ops:
                op_mode = True
                k = len(stream) - 1 - i
                op = c
            else:
                op_mode = False

            if k is not None and not op_mode:
                break

        if k is None:
            raise ParseException(f"expected binary expression in {stream[0].meta}")

        return op, stream[:k], stream[k + 1:]

    def parse_record_name(self, stream):
        if not(type(stream) is list and stream):
            raise ParseException()

        op, stream1, stream2 = self.pre_parse_binary(stream, ['.'])

        if op != '.':
            raise ParseException(f"expected '.' in {stream[0].meta}")

        if not(len(stream2) == 1 and type(stream2[0]) is TerminalSymb and self.is_var_token(stream2[0])):
            raise ParseException(f"expected var name after dot in {stream[0].meta}")

        res = ast.ValueAtName(self.parse_expression(stream1), ast.Const(stream2[0].visual())).add_meta(stream2[0].meta)
        return res

    def try_parse_record_name(self, stream):
        try:
            return self.parse_record_name(stream)
        except ParseException as e:
            return None

    def parse_binary(self, stream, ops):
        if not (type(stream) is list and stream):
            raise ParseException()

        op, stream1, stream2 = self.pre_parse_binary(stream, ops)
        # print(op)
        return self.binary_operators[op](self.parse_expression(stream1), self.parse_expression(stream2)).add_raw_str(op.visual())

    def try_binary_parse(self, exp, ops):
        try:
            return self.parse_binary(exp, ops)
        except ParseException as e:
            return None

    def parse_call(self, stream):
        if not (type(stream) is list and stream):
            raise ParseException()

        expression = self.parse_expression(stream[:-1])

        if not(type(stream[-1]) is BracketSymb and stream[-1].opening == '('):
            raise ParseException(f"'(' expected in {stream[-1].meta}")

        args = self.parse_list(stream[-1].value, ',')
        expressions = []
        for arg in args:
            exp = self.parse_expression(arg.value)
            exp.meta = arg.meta
            expressions.append(exp)

        res = ast.Call(expression, *expressions).add_meta(stream[0].meta)

        if type(expression) is ast.Var:
            direct_fun_name = expression.term.visual()
            lead = self.build_calling_name(expression.term)

            if direct_fun_name in builtin.functions:
                return builtin.functions[direct_fun_name](*expressions).add_raw_str(direct_fun_name)

            if direct_fun_name == '__api__':
                return ast.ApiCall(*expressions).add_meta(expression.term.meta)

            res.add_lead(lead)

        return res

    def try_parse_call(self, stream):
        try:
            return self.parse_call(stream)
        except ParseException as e:
            return None

    def parse_value_at(self, stream):
        if not (type(stream) is list and stream):
            raise ParseException()

        expression = self.parse_expression(stream[:-1])

        if not(type(stream[-1]) is BracketSymb and stream[-1].opening == '['):
            raise ParseException(f"'[' expected in {stream[-1].meta}")

        args = self.parse_list(stream[-1].value, ',')
        expressions = []
        for arg in args:
            exp = self.parse_expression(arg.value)
            exp.meta = arg.meta
            expressions.append(exp)
        #index_expression = self.parse_expression(stream[-1].value)

        return ast.ValueAt(expression, *expressions).add_meta(stream[0].meta)

    def try_parse_value_at(self, stream):
        try:
            return self.parse_value_at(stream)
        except ParseException as e:
            return None

    def build_calling_name(self, term):
        lead = term.meta.lead
        if lead is None:
            res = level.core.parser.linker.Lead(key=term.visual(), name=term.visual())
        else:
            if lead.name is None:
                alternative_name = lead.key + ':' + term.visual()
            else:
                if lead.name == '*':
                    alternative_name = term.visual()
                else:
                    alternative_name = lead.name + ':' + term.visual()

            res = level.core.parser.linker.Lead(key=lead.name + ":" + term.visual(), name=alternative_name)

        return res

    def parse_type_expression(self, stream):
        # print(stream)
        if not stream:
            raise ParseException()

        if type(stream) is TerminalSymb:
            if self.is_var_token(stream):
                key = stream.visual()
                if key in builtin.translate_simple_types:
                    return ast.Type(stream.visual()).add_meta(stream.meta)
                else:
                    return ast.Type(self.build_calling_name(stream).name).add_meta(stream.meta)

        if type(stream) is BracketSymb or type(stream) is ArgSymb:
            return self.parse_type_expression(stream.value)

        if type(stream) is list and stream:
            if len(stream) == 1:
                return self.parse_type_expression(stream[0])

        res = self.try_parse_type_function(stream)
        if res is not None:
            return res

        raise ParseException(f"badly formed type expression in {meta(stream)}")

    def parse_type_function(self, stream):
        if not(type(stream) is list and stream):
            raise ParseException()

        if (type(stream[0]) is not TerminalSymb) or (stream[0].visual().isdigit()):
            raise ParseException(f"type function name expected in {stream[0].meta}")

        fun_name = stream[0].visual()

        if not(type(stream[1]) is BracketSymb and stream[1].opening == '('):
            raise ParseException(f"'(' expected in {stream[1].meta}")

        args = self.parse_list(stream[1].value, ',')
        expressions = []

        if fun_name == 'array' and len(args) == 2:
            exp = self.parse_type_expression(args[0].value)
            if type(args[1].value[0]) is TerminalSymb and args[1].value[0].visual().isdigit():
                return ast.ArrayType(exp, ast.Const(int(args[1].value[0].visual())).add_meta(args[1].value[0].meta)).add_meta(stream[0].meta)
            else:
                raise ParseException(f"badly formed array type in {stream[1].meta}")

        if fun_name == 'ref':
            if args:
                expressions.append(self.parse_type_expression(args[0].value))
            return ast.RefType(*expressions).add_meta(stream[0].meta)

        if fun_name == "rec":
            if args:
                statements = []
                for arg in args:
                    statements.append(self.parse_var_statement(arg.value))
                return ast.RecType(*statements).add_meta(stream[0].meta)

        raise ParseException(f"badly formed type function in {stream[0].meta}")

    def try_parse_type_function(self, stream):
        try:
            return self.parse_type_function(stream)
        except ParseException as e:
            return None

    def is_var_token(self, t):
        for c in t.value:
            if not (c.c.isalnum() or c == '_' or c == ':'):
                return False
        return True

    def composed_const(self, stream):
        if type(stream) is not list:
            raise ParseException(f"invalid const value in {meta(stream)}")
        for s in stream:
            if type(s) is not TerminalSymb:
                raise ParseException(f"invalid const value in {meta(stream[0])}")

        candidate = "".join(map(lambda k: k.visual(), stream))

        if re.match(r"^([+-]?)\d+$", candidate, re.MULTILINE) is not None:
            return ast.Const(int(candidate))

        if re.match(r"^0x[\da-fA-F]+$", candidate, re.MULTILINE) is not None:
            return ast.Const(ast.U64ConstType(eval(candidate)))

        m = re.match(r"^(?P<significand>[+-]?\d+(\.\d+)?)(e(?P<exponent>[+-]\d+))?$", candidate, re.MULTILINE)
        if m is not None:
            exponent = m.group('exponent')
            v = float80(m.group('significand'), int(exponent) if exponent is not None else 0)
            return ast.Const(ast.FloatConstType(struct.pack("QH", v[1], v[0])))

        raise ParseException(f"invalid const value in {meta(stream[0])}")

    def parse_const(self, stream):
        # print(stream)
        if type(stream) is StringSymb:
            return ast.Const(bytes(stream.string(), encoding='utf-8')).add_meta(stream.meta)

        if type(stream) is TerminalSymb:
            if stream.visual().isdigit():
                return ast.Const(int(stream.visual())).add_meta(stream.meta)

            res = builtin.translate_reserved_const(stream.visual())
            if res is not None:
                return ast.Const(res).add_meta(stream.meta)

        return self.composed_const(stream)

        #raise ParseException(f"invalid const value in {meta(stream)}")


    def parse_expression(self, stream):
        if not stream:
            raise ParseException()

        res = self.try_parse(self.parse_const, stream)
        if res is not None:
            return res

        if type(stream) is TerminalSymb:
            if self.is_var_token(stream):
                return ast.Var(stream.visual()).add_meta(stream.meta).add_term(stream)

        if type(stream) is BracketSymb or type(stream) is ArgSymb:

            if type(stream) is BracketSymb and stream.opening == '{':
                # print(stream)
                return ast.Ref(self.parse_expression(stream.value)).add_meta(stream.meta)

            if type(stream) is BracketSymb and stream.opening == '[':
                # print(stream)
                return ast.Val(self.parse_expression(stream.value)).add_meta(stream.meta)

            if not stream.value:
                # print(type(stream))
                raise ParseException(f"expected expression in {meta(stream)}")

            return self.parse_expression(stream.value)


        if type(stream) is list and stream:
            if len(stream) == 1:
                return self.parse_expression(stream[0])

            res = self.try_binary_parse(stream, ['and', 'or'])
            if res is not None:
                return res

            res = self.try_binary_parse(stream, ['!=', '==', '<', '>', '<=', '>='])
            if res is not None:
                return res

            res = self.try_binary_parse(stream, ['+', '-'])
            if res is not None:
                return res

            res = self.try_binary_parse(stream, ['*', '/', '%'])
            if res is not None:
                return res

            for op in self.unary_operators:
                res = self.try_parse_unary(stream, op)
                if res is not None:
                    return res

            res = self.try_parse_record_name(stream)
            if res is not None:
                return res

            res = self.try_parse_value_at(stream)
            if res is not None:
                return res

            res = self.try_parse_call(stream)
            if res is not None:
                return res

            # res = self.try_parse_function_call(stream)
            # if res is not None:
            #     return res

            raise ParseException(f"badly formed expression '{stream[0]}' in {stream[0].meta}")


        raise ParseException(f"unexpected expression error in {meta(stream)}")

    def find(self, stream, term):
        for i, c in enumerate(stream):
            if c == term:
                return i

        return len(stream)

    def parse_statement_function(self, stream):
        if not(type(stream) is list and stream):
            raise ParseException()

        fun_name = stream[0].visual()

        args = self.parse_list(stream[1:], ',')
        expressions = []
        for arg in args:
            exp = self.parse_expression(arg.value)
            exp.meta = arg.meta
            expressions.append(exp)

        fun, n = builtin.statement_functions[fun_name]

        if n is not None:
            if n != len(expressions):
                ParseException(f"{n} arguments expected after '{fun_name}' in {stream[0].meta}")

        res = fun(*expressions)
        res.meta = stream[0].meta
        return res

    def parse_statement_operator(self, op, stream):
        if not (type(stream) is list and stream):
            raise ParseException()

        exps = self.parse_list(stream, op)
        if len(exps) == 2:
            exp1 = self.parse_expression(exps[0])
            exp2 = self.parse_expression(exps[1])
            res = builtin.statement_operators[op](exp1, exp2)
            res.meta = stream[0].meta
            return res
        else:
            raise ParseException(f"expected two expressions for '{op}' in {stream[0].meta}")

    def try_parse_statement_operator(self, op, stream):
        try:
            return self.parse_statement_operator(op, stream)
        except ParseException as e:
            return None

    def parse_type_statement(self, key, stream, grammar_type, var_type):
        if not (type(stream) is list and stream):
            raise ParseException()

        if stream and stream[-1] == ';':
            stream = stream[:-1]

        if type(stream[0]) is TerminalSymb and stream[0] == key:
            #print(stream)
            if 5 >= len(stream) > 1 and type(stream[1]) is TerminalSymb and self.is_var_token(stream[1]):
                if len(stream) > 3:
                    exp_type = self.parse_type_expression(stream[3:])
                else:
                    raise ParseException(f"expected type expression in {meta(stream)}")
                return grammar_type(var_type(self.build_calling_name(stream[1])), exp_type)
            else:
                raise ParseException(f"badly formed type in '{key}' statement in {stream[0].meta}")
        else:
            raise ParseException(f"expected '{key}' statement in {stream[0].meta}")

    def parse_var_statement(self, stream):
        if not (type(stream) is list and stream):
            raise ParseException()

        if stream and stream[-1] == ';':
            stream = stream[:-1]

        if type(stream[0]) is TerminalSymb and stream[0] == 'var':
            if len(stream) > 3 and type(stream[1]) is TerminalSymb and self.is_var_token(stream[1]):
                const = ast.ConstVoid()
                type_expression_index = 3
                as_index = 2
                if type(stream[2]) is TerminalSymb and stream[2] == '=':
                    as_index = self.find(stream, "as")
                    const = self.parse_const(stream[3:as_index])
                    type_expression_index = as_index + 1
                    # as_index = 4

                if len(stream) > as_index and type(stream[as_index]) is TerminalSymb and stream[as_index] == 'as':
                    if len(stream) > type_expression_index:
                        exp_type = self.parse_type_expression(stream[type_expression_index:])
                    else:
                        raise ParseException(f"expected type expression in {meta(stream)}")
                    return ast.InitWithType(ast.Var(stream[1].visual()).add_meta(stream[1].meta), exp_type, const).add_meta(stream[0].meta)
                else:
                    if len(stream) == as_index:
                        return ast.InitWithType(ast.Var(stream[1].visual()).add_meta(stream[1].meta), ast.TypeVoid(), const).add_meta(stream[0].meta)
                    else:
                        raise ParseException(f"badly formed type in 'var' statement in {stream[-1].meta}")
            else:
                raise ParseException(f"badly formed type in 'var' statement in {stream[0].meta}")
        else:
            raise ParseException(f"expected 'var' statement in {stream[0].meta}")

    def parse_statement(self, stream):
        # print(stream)
        if not(type(stream) is list and stream):
            raise ParseException()

        limit = self.find(stream, ';')

        if stream and type(stream[0]) is TerminalSymb:
            terminal = stream[0]

            if terminal in builtin.statement_functions:
                return limit, self.parse_statement_function(stream[:limit])

            if terminal == 'var':
                return limit, self.parse_var_statement(stream[:limit])

            if terminal == 'if':
                return self.parse_if_statement(stream, limit)

            if terminal == 'while':
                return self.parse_while_statement(stream, limit)

            if terminal == 'for':
                return self.parse_for_statement(stream, limit)

        if stream and type(stream[0]) is TerminalSymb and self.is_var_token(stream[0]):
            if len(stream) > 2 and type(stream[1]) is TerminalSymb and stream[1].visual() == '$=':
                var_name = stream[0].visual()
                exp = self.parse_expression(stream[2:limit])
                exp.meta = stream[1].meta
                return limit, ast.Identify(ast.Var(var_name).add_meta(stream[2].meta), exp).add_meta(stream[0].meta)

        if limit is not None:
            for op in builtin.statement_operators:
                res = self.try_parse_statement_operator(op, stream[:limit])
                if res is not None:
                    return limit, res.add_meta(stream[0].meta)

        raise ParseException(f"unexpected statement in {stream[0].meta}")

    def parse_if_statement(self, stream, limit):
        if not(type(stream) is list and stream):
            raise ParseException()

        if len(stream) > 1 and type(stream[1]) is BracketSymb:
            condition = self.parse_expression(stream[1])
            if len(stream) > 2 and type(stream[2]) is BracketSymb:
                if_statement_list = self.parse_statement_list(stream[2].value)
                if len(stream) > 3 \
                        and type(stream[3]) is TerminalSymb \
                        and stream[3] == 'else':
                    if len(stream) > 4 and type(stream[4]) is BracketSymb:
                        else_statement_list = self.parse_statement_list(stream[4].value)
                        return 4 if (limit is None or limit > 5) else limit, ast.IfElse(condition, if_statement_list,
                                                                                        else_statement_list).add_meta(stream[0].meta)
                    else:
                        raise ParseException(f"'{{' expected after 'else' in {stream[3].meta}")
                else:
                    return 2 if (limit is None or limit > 3) else limit, ast.IfElse(condition, if_statement_list,
                                                                                    ast.StatementList()).add_meta(stream[0].meta)

            else:
                raise ParseException(f"'{{' expected after 'if' in {stream[1].meta}")
        else:
            raise ParseException(f"'(' expected after 'if' in {stream[0].meta}")

    def parse_while_statement(self, stream, limit):
        if not (type(stream) is list and stream):
            raise ParseException()

        if len(stream) > 0 and type(stream[1]) is BracketSymb:
            condition = self.parse_expression(stream[1])
            if len(stream) > 1 and type(stream[2]) is BracketSymb:
                statement_list = self.parse_statement_list(stream[2].value)
                return 2 if (limit is None or limit > 3) else limit, ast.While(condition, statement_list).add_meta(stream[0].meta)
            else:
                raise ParseException(f"'{{' bracket expected after 'while' in {stream[1].meta}")
        else:
            raise ParseException(f"'(' expected after 'while' in {stream[0].meta}")

    def parse_for_statement(self, stream, limit):
        if not (type(stream) is list and stream):
            raise ParseException()

        if len(stream) > 0 and type(stream[1]) is BracketSymb:
            args = self.parse_list(stream[1].value, ';')
            # print(args)
            if len(args) != 3:
                raise ParseException(f"badly formed if statement in {stream[1].meta}")
            _, init_statement = self.parse_statement(args[0].value)
            condition = self.parse_expression(args[1].value)
            _, final_statement = self.parse_statement(args[2].value)
            # print(init_statement, condition, final_statement)
            if len(stream) > 1 and type(stream[2]) is BracketSymb:
                statement_list = self.parse_statement_list(stream[2].value)
                return 2 if (limit is None or limit > 3) else limit, ast.For(init_statement, condition, final_statement,
                                                                             statement_list).add_meta(stream[0].meta)
            else:
                raise ParseException(f"'{{'expected after 'for' in {stream[1].meta}")
        else:
            raise ParseException(f"'(' expected after 'for' in {stream[0].meta}")

    def parse_statement_list(self, stream):
        if not stream:
            ParseException()

        if type(stream) is list and len(stream) == 0:
            return ast.StatementList()

        meta = stream[0].meta

        statement_list = []
        while stream:
            i, statement = self.parse_statement(stream)
            statement_list.append(statement)
            if i is None:
                break
            stream = stream[i + 1:]

        return ast.StatementList(*statement_list).add_meta(meta)

    def parse_def(self, stream, method=False):
        if not (type(stream) is list and stream):
            raise ParseException()

        code_bracket_index = self.find(stream, BracketSymb(opening='{', closing='}', value=None))
        # print(stream)
        # print(code_bracket_index)
        type_index = 2

        variables = []
        return_type = ast.Type('int').add_meta(stream[0].meta)

        if stream and type(stream[0]) is TerminalSymb:
            if not method:
                func_name = self.build_calling_name(stream[0])
            else:
                direct_fun_name = stream[0].visual()
                func_name = level.core.parser.linker.Lead(direct_fun_name, direct_fun_name)
        else:
            if stream and type(stream[0]) is BracketSymb and stream[0].opening == '[':
                # print(stream[0])
                direct_fun_name = '[]'
                func_name = level.core.parser.linker.Lead(direct_fun_name, direct_fun_name)
            else:
                raise ParseException(f"badly formed function definition in {stream[0].meta}")

        if len(stream) >= 3 and type(stream[1]) is BracketSymb:
            type_index = 3;
            args = self.parse_list(stream[1].value, ',')
            variables = []
            for arg in args:
                variables.append(self.parse_var_statement(arg.value))

        if len(stream) > type_index and stream[type_index:code_bracket_index]:
            return_type = self.parse_type_expression(stream[type_index:code_bracket_index])

        if stream and type(stream[code_bracket_index]) is BracketSymb:
            statements = self.parse_statement_list(stream[code_bracket_index].value)
            return ast.SubroutineDef(func_name, ast.VarList(*variables).add_meta(stream[0].meta), statements, return_type).add_meta(stream[0].meta)

        #else:
        raise ParseException(f"badly formed function definition in {stream[0].meta}")

    # def parse_defs(self, stream):
    #     defs = []
    #
    #     if stream:
    #         meta = stream[0].meta
    #     else:
    #         meta = None
    #
    #     while(stream and type(stream[0]) is TerminalSymb and stream[0] == 'sub'):
    #         code_bracket_index = self.find(stream, BracketSymb(opening='{', closing='}', value=None))
    #         def_ = self.parse_def(stream[1:code_bracket_index + 1])
    #         stream = stream[code_bracket_index + 1:]
    #         defs.append(def_)
    #
    #     return ast.DefBlock(*defs).add_meta(meta)

    def parse_types(self, stream):
        if not (type(stream) is list and stream):
            raise ParseException()

        meta = stream[0].meta

        types = []
        while (stream and type(stream[0]) is TerminalSymb and stream[0] == 'type'):
            limit = self.find(stream[1:], 'type') + 1
            # print(limit)
            type_statement = self.parse_type_statement('type', stream[:limit], ast.AssignType, ast.Type)
            types.append(type_statement)
            stream = stream[limit:]

        return ast.AssignTypeList(*types).add_meta(meta)

    def parse_block(self, key, stream):
        if not (type(stream) is list and stream):
            raise ParseException("nothing to parse")

        if len(stream) >= 2 and type(stream[0]) is TerminalSymb and stream[0] == key and type(stream[1]) is BracketSymb:
            return stream[2:], stream[1].value
        else:
            raise ParseException(f"badly formed '{key}' block in {stream[0].meta}")

    def parse_program(self, stream):
        if type(stream) is list and not stream:
            raise ParseException('nothing to parse')

        type_defs = []
        subroutines = []

        while (stream and type(stream[0]) is TerminalSymb and stream[0] in {'sub', 'type', 'method'}):
            # print(stream[0])
            if stream[0] == 'sub':
                code_bracket_index = self.find(stream, BracketSymb(opening='{', closing='}', value=None))
                def_ = self.parse_def(stream[1:code_bracket_index + 1])
                stream = stream[code_bracket_index + 1:]
                subroutines.append(def_)
                continue

            if stream[0] == 'method':
                code_bracket_index = self.find(stream, BracketSymb(opening='{', closing='}', value=None))
                def_ = self.parse_def(stream[1:code_bracket_index + 1], method=True)
                stream = stream[code_bracket_index + 1:]
                subroutines.append(def_)
                continue

            if stream[0] == 'type':
                a = self.find(stream[1:], 'type') + 1
                b = self.find(stream[1:], 'sub') + 1
                c = self.find(stream[1:], 'entry') + 1
                d = self.find(stream[1:], 'method') + 1
                limit = min(a, b, c, d)
                # print(limit)
                type_statement = self.parse_type_statement('type', stream[:limit], ast.AssignType, ast.Type)
                type_defs.append(type_statement)
                stream = stream[limit:]
                continue

        if type(stream) is list and not stream:
            raise ParseException(f"missed entry block")

        meta = stream[0].meta

        stream, program_block = self.parse_block('entry', stream)
        statements = self.parse_statement_list(program_block)
        return ast.Program(ast.AssignTypeList(*type_defs), ast.DefBlock(*subroutines), statements).add_meta(meta)
