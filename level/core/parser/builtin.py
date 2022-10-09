import level.core.ast as ast

default_modules = [
    #("stdlib:sys:context", "stdlib:sys:context")
]

binary_operators = {
    '+' : ast.Add,
    'shift' : ast.AddNoOverride,
    '-' : ast.Sub,
    '*' : ast.Mul,
    '**' : ast.Pow,
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

no_override_binary = set([ast.AddNoOverride])

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
    'round' : ast.Round,
    'log2' : ast.Log2,
    'log10' : ast.Log10,
    'log' : ast.Log,
    'exp' : ast.Exp,
    'pow10' : ast.Pow10,
    'pow2' : ast.Pow2,
    'typeid' : ast.TypeId,
    'sizeof' : ast.SizeOf
}


statement_functions = {
    'return': (ast.Return, None),
    'echo' : (ast.Echo, 1),
    'break': (ast.Break, 0),
    'continue': (ast.Continue, 0),
    'exec': (ast.Exec, 1),
    'inc' : (ast.Inc, None),
    'dec' : (ast.Dec, None)
}

statement_operators = {
    '<-' : ast.AssignNoOverride,
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
    'ref' : 'Ref',
    '__ref__' : 'Ref',
    'object': 'Object',
    'swap': 'Swap'
}

default_return_type = 'int'

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