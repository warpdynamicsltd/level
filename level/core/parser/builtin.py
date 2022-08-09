import level.core.ast as ast

binary_operators = {
    '+' : ast.Add,
    '-' : ast.Sub,
    '*' : ast.Mul,
    '/' : ast.Div,
    '%' : ast.Mod,
    '==': ast.Eq,
    '!=': ast.Neq,
    '<' : ast.Lt,
    '>' : ast.Gt,
    '<=': ast.Le,
    '>=': ast.Ge,
    'and': ast.And,
    'or': ast.Or}

unary_operators = {
    '+': ast.Plus,
    '-': ast.Minus,
    'not': ast.Not,
    'ref': ast.Ref,
    'val': ast.Val,
    'abs': ast.Abs,
    'sgn': ast.Sgn,
    'typeid': ast.TypeId}


functions = {
    'ref': ast.Ref,
    'val': ast.Val,
    'abs': ast.Abs,
    'sgn': ast.Sgn,
    'sin': ast.Sin,
    'cos': ast.Cos,
    'tan': ast.Tan,
    'cot': ast.Cot,
    'sqrt': ast.Sqrt,
    'floor': ast.Floor,
    'ceil' : ast.Ceil,
    'typeid' : ast.TypeId
}


statement_functions = {
    'return': (ast.Return, None),
    'echo' : (ast.Echo, 1),
    'break': (ast.Break, 0),
    'exec': (ast.Exec, 1),
    'inc' : (ast.Inc, 1),
    'dec' : (ast.Dec, 1)
}

statement_operators = {
    '<-' : ast.Assign,
    '=' : ast.Assign,
}

translate_simple_types = {
    'u32': 'U32',
    'i32' : 'I32',
    'u64' : 'U64',
    'i64' : 'I64',
    'int' : 'I64',
    'float': 'Float',
    'bool': 'Bool',
    'byte': 'Byte',
    'ref' : 'Ref'
}

class BuiltinValue:
    def __init__(self, value):
        self.value = value

class BuiltinFloat(BuiltinValue):
    pass


def translate_reserved_const(const):
    if const == 'true':
        return True
    if const == 'false':
        return False
    if const == 'float:pi':
        return BuiltinFloat('pi')

    return None