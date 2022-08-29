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
    'or': ast.Or,
    '&': ast.BAnd,
    '|': ast.BOr,
    '^': ast.BXor,
    '>>': ast.RShift,
    '<<': ast.LShift
}

unary_operators = {
    '+': ast.Plus,
    '-': ast.Minus,
    'not': ast.Not,
    '~'  : ast.BNot,
    'ref': ast.Ref,
    'val': ast.Val,
    'abs': ast.Abs,
    'sgn': ast.Sgn,
    'typeid': ast.TypeId,
    'sizeof': ast.SizeOf}


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
    'log2' : ast.Log2,
    'typeid' : ast.TypeId,
    'sizeof' : ast.SizeOf
}


statement_functions = {
    'return': (ast.Return, None),
    'echo' : (ast.Echo, 1),
    'break': (ast.Break, 0),
    'continue': (ast.Continue, 0),
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

class BuiltinRef(BuiltinValue):
    pass

def translate_reserved_const(const):
    if const == 'true':
        return True
    if const == 'false':
        return False
    if const == 'float:pi':
        return BuiltinFloat('pi')
    if const == 'null':
        return BuiltinRef('null')

    return None