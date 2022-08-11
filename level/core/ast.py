import copy

class GrammarTreeError(Exception):
    pass

class U64ConstType:
    def __init__(self, value):
        self.value = value

    def __int__(self):
        return self.value

class FloatConstType:
    def __init__(self, value):
        self.value = value

    def __bytes__(self):
        return self.value

def istype(e, c):
    return issubclass(type(e), c) or (type(e) is MetaVar)

class MetaVar:
    def __init__(self, value=None):
        self.val = value

    def __repr__(self):
        return repr(self.val)

class Element:
    def __init__(self, name, *args):
        """
        Parameters
        ----------
        name :
        args : list(Element)
        """
        self.name = name
        self.args = args
        self.meta = None
        self.calling_name = None
        self.raw_str = None
        self.term = None

    def __lshift__(self, element):
        if type(self.name) is MetaVar:
            self.name.val = element.name
        else:
            self.name = element.name

        n_missing = len(element.args) - len(self.args)

        if n_missing > 0:
            for i in range(n_missing):
                self.args.append(MetaVar())

        for i, arg in enumerate(self.args):
            arg.val = element.args[i]

    def __repr__(self):
        return f"{self.name}({self.args})"

    def add_meta(self, meta):
        self.meta = meta
        return self

    def add_calling_name(self, calling_name):
        self.calling_name = calling_name
        return self

    def add_raw_str(self, raw_str):
        self.raw_str = raw_str
        return self

    def add_term(self, term):
        self.term = term
        return self

    def clone(self):
        x = copy.copy(self)
        x.name = self.name
        x.meta = self.meta
        x.calling_name = self.calling_name
        x.raw_str = self.raw_str
        x.term = self.term
        x.args = []
        for arg in self.args:
            x.args.append(arg.clone())

        return x


class Null(Element):
    pass

class Expression(Element):
    pass

class TypeExpression(Element):
    pass

class TypeTemplateExpression(Element):
    pass

class TypeVoid(TypeExpression):
    def __init__(self):
        Type.__init__(self, None)

class AtomicExpression(Expression):
    def __init__(self, name):
        Expression.__init__(self, name)

class Var(AtomicExpression):
    def __repr__(self):
        return f"Var({self.name})"

class Const(AtomicExpression):
    def __repr__(self):
        return f"Const({self.name})"

class ConstVoid(Const):
    def __init__(self):
        Const.__init__(self, None)

class CompoundExpression(Expression):
    def __init__(self, name, *expressions):
        for e in expressions:
            if not (istype(e, CompoundExpression) or istype(e, Expression)):
                raise GrammarTreeError()

        Expression.__init__(self, name, *expressions)


class UnaryExpression(CompoundExpression):
    def __init__(self, name, expression):
        if not istype(expression, Expression):
            raise GrammarTreeError
        CompoundExpression.__init__(self, name, expression)

class BinaryExpression(CompoundExpression):
    def __init__(self, name, *expressions):
        if not len(expressions) == 2:
            raise GrammarTreeError
        CompoundExpression.__init__(self, name, *expressions)

class Statement(Element):
    pass

class StatementList(Element):
    def __init__(self, *statements):
        for s in statements:
            if not istype(s, Statement):
                raise GrammarTreeError()

        Element.__init__(self, 'StatementList', *statements)

class Program(Element):
    def __init__(self, assign_type_block, global_inits, def_block, code_block):
        if not (istype(assign_type_block, AssignTypeList) and
                istype(global_inits, GlobalBlock) and
                istype(def_block, DefBlock) and
                istype(code_block, StatementList)):
            raise GrammarTreeError()

        Element.__init__(self, 'Program', assign_type_block, global_inits, def_block, code_block)

class DefBlock(Element):
    def __init__(self, *defs):
        for d in defs:
            if not istype(d, SubroutineDef):
                raise GrammarTreeError()

        Element.__init__(self, 'DefBlock', *defs)

class GlobalBlock(Element):
    def __init__(self, *global_inits):
        for g in global_inits:
            if not istype(g, InitGlobalWithType):
                raise GrammarTreeError()

        Element.__init__(self, 'GlobalBlock', *global_inits)

class VarList(Element):
    def __init__(self, *vars):
        for v in vars:
            if not (istype(v, InitWithType) or istype(v, TypeExpression)):
                raise GrammarTreeError()

        Element.__init__(self, 'VarList', *vars)

class SubroutineDef(Element):
    def __init__(self, name, var_list, statement_list, return_type_exp):
        if not (istype(var_list, VarList) and istype(statement_list, StatementList) and istype(return_type_exp, TypeExpression)):
            raise GrammarTreeError()
        Element.__init__(self, name, var_list, statement_list, return_type_exp)

class SubroutineCall(Expression):
    def __init__(self, name, *expressions):
        for e in expressions:
            if not (istype(e, Expression) or istype(e, TypeExpression)):
                raise GrammarTreeError()
        Element.__init__(self, name, *expressions)

class Call(Expression):
    def __init__(self, expression, *expressions):
        if not istype(expression, Expression):
            raise GrammarTreeError()
        for e in expressions:
            if not (istype(e, Expression) or istype(e, TypeExpression)):
                raise GrammarTreeError()
        Element.__init__(self, 'Call', expression, *expressions)


class ApiCall(Expression):
    def __init__(self, *expressions):
        for e in expressions:
            if not istype(e, Expression):
                raise GrammarTreeError()
        Element.__init__(self, 'ApiCall', *expressions)

class ValueAt(Expression):
    def __init__(self, expression, *expressions):
        if not istype(expression, Expression):
            raise GrammarTreeError()
        for e in expressions:
            if not istype(e, Expression):
                raise  GrammarTreeError()
        Expression.__init__(self, 'ValueAt', expression, *expressions)

class ValueAtName(Expression):
    def __init__(self, expression, name):
        if not(istype(expression, Expression) and istype(name, Const)):
            raise GrammarTreeError()
        Expression.__init__(self, 'ValueAt', expression, name)

class Ref(Expression):
    def __init__(self, expression):
        if not(istype(expression, Expression)):
            raise GrammarTreeError()
        Expression.__init__(self, 'Ref', expression)

class Val(Expression):
    def __init__(self, expression):
        if not(istype(expression, Expression)):
            raise GrammarTreeError()
        Expression.__init__(self, 'Val', expression)


class ConditionStatement(Statement):
    def __init__(self, name, expression, statement_list1, statement_list2):
        if not (istype(expression, Expression) and istype(statement_list1, StatementList)) and istype(statement_list2, StatementList):
            raise GrammarTreeError()
        Statement.__init__(self, name, expression, statement_list1, statement_list2)

"""
Level key words 
"""

"""
    Statements
"""

class IfElse(Statement):
    def __init__(self, expression, if_statement_list, else_statement_list):
        if not(istype(expression, Expression) and istype(if_statement_list, StatementList) and istype(else_statement_list, StatementList)):
            raise GrammarTreeError()
        Statement.__init__(self, 'IfElse', expression, if_statement_list, else_statement_list)

class While(Statement):
    def __init__(self, expression, statement_list1):
        if not(istype(expression, Expression) and istype(statement_list1, StatementList)):
            raise GrammarTreeError()
        Statement.__init__(self, 'While', expression, statement_list1)

class For(Statement):
    def __init__(self, init_statement, condition_expression, final_statement, for_statement_list):
        if not(
                istype(init_statement, Statement) and \
                istype(condition_expression, Expression) and \
                istype(final_statement, Statement) and \
                istype(for_statement_list, StatementList) \
            ):
            raise GrammarTreeError()
        Statement.__init__(self, 'For', init_statement, condition_expression, final_statement, for_statement_list)

class Return(Statement):
    def __init__(self, *expression):
        Statement.__init__(self, 'Return', *expression)

class Exec(Statement):
    def __init__(self, expression):
        if not istype(expression, Expression):
            raise GrammarTreeError()
        Statement.__init__(self, 'Exec', expression)

class Identify(Statement):
    def __init__(self, var, expression):
        if not(istype(var, Var) and istype(expression, Expression)):
            raise GrammarTreeError()
        Statement.__init__(self, 'Assign', var, expression)


class Assign(Statement):
    def __init__(self, var_expression, expression):
        if not(istype(var_expression, Expression) and istype(expression, Expression)):
            raise GrammarTreeError()
        Statement.__init__(self, 'Assign', var_expression, expression)

class AssignAt(Statement):
    def __init__(self, var, index_expression, expression):
        if not(istype(var, Var) and istype(index_expression, Expression) and istype(expression, Expression)):
            raise GrammarTreeError()
        Statement.__init__(self, 'AssignAt', var, index_expression, expression)

class Init(Statement):
    def __init__(self, var):
        if not(istype(var, Var)):
            raise GrammarTreeError()
        Statement.__init__(self, 'Init', var)

class InitWithType(Statement):
    def __init__(self, var, type_expression, const):
        if not(istype(var, Var) and istype(type_expression, TypeExpression) and istype(const, Const)):
            raise GrammarTreeError()
        Statement.__init__(self, 'InitWithType', var, type_expression, const)

class InitGlobalWithType(Statement):
    def __init__(self, var, type_expression, const):
        if not(istype(var, Var) and istype(type_expression, TypeExpression) and istype(const, Const)):
            raise GrammarTreeError()
        Statement.__init__(self, 'InitGlobalWithType', var, type_expression, const)

class InitRef(Statement):
    def __init__(self, var):
        if not(istype(var, Var)):
            raise GrammarTreeError()
        Statement.__init__(self, 'InitRef', var)

class InitArray(Statement):
    def __init__(self, var, c):
        if not(istype(var, Var)) and not(istype(c, Const)):
            raise GrammarTreeError()
        Statement.__init__(self, 'InitArray', var, c)

class Echo(Statement):
    def __init__(self, expression):
        if not(istype(expression, Expression)):
            raise GrammarTreeError
        Statement.__init__(self, 'Echo', expression)

class EmptyStatement(Statement):
    def __init__(self):
        Statement.__init__(self, 'EmptyStatement')

class Break(Statement):
    def __init__(self):
        Statement.__init__(self, 'Break')

class Inc(Statement):
    def __init__(self, a):
        if not(istype(a, Expression)):
            raise GrammarTreeError()
        Statement.__init__(self, 'Inc', a)

class Dec(Statement):
    def __init__(self, a):
        if not(istype(a, Expression)):
            raise GrammarTreeError()
        Statement.__init__(self, 'Dec', a)



"""
    Expressions
"""
class TypeId(UnaryExpression):
    def __init__(self, a):
        CompoundExpression.__init__(self, 'TypeId', a)

class SizeOf(UnaryExpression):
    def __init__(self, a):
        CompoundExpression.__init__(self, 'SizeOf', a)


class Minus(UnaryExpression):
    def __init__(self, a):
        CompoundExpression.__init__(self, 'Minus', a)

class Plus(UnaryExpression):
    def __init__(self, a):
        CompoundExpression.__init__(self, 'Plus', a)

class Not(UnaryExpression):
    def __init__(self, a):
        CompoundExpression.__init__(self, 'Not', a)

class BNot(UnaryExpression):
    def __init__(self, a):
        CompoundExpression.__init__(self, 'BNot', a)

class Abs(UnaryExpression):
    def __init__(self, a):
        CompoundExpression.__init__(self, 'Abs', a)

class Sgn(UnaryExpression):
    def __init__(self, a):
        CompoundExpression.__init__(self, 'Sgn', a)

class And(BinaryExpression):
    def __init__(self, a, b):
        BinaryExpression.__init__(self, 'And', a, b)

class Or(BinaryExpression):
    def __init__(self, a, b):
        BinaryExpression.__init__(self, 'Or', a, b)

class Add(BinaryExpression):
    def __init__(self, a, b):
        BinaryExpression.__init__(self, 'Add', a, b)

class Mul(BinaryExpression):
    def __init__(self, a, b):
        BinaryExpression.__init__(self, 'Mul', a, b)

class Sub(BinaryExpression):
    def __init__(self, a, b):
        BinaryExpression.__init__(self, 'Sub', a, b)

class Div(BinaryExpression):
    def __init__(self, a, b):
        BinaryExpression.__init__(self, 'Div', a, b)

class Mod(BinaryExpression):
    def __init__(self, a, b):
        BinaryExpression.__init__(self, 'Mod', a, b)

class Eq(BinaryExpression):
    def __init__(self, a, b):
        BinaryExpression.__init__(self, 'Eq', a, b)

class Neq(BinaryExpression):
    def __init__(self, a, b):
        BinaryExpression.__init__(self, 'Neq', a, b)

class Le(BinaryExpression):
    def __init__(self, a, b):
        BinaryExpression.__init__(self, 'Le', a, b)

class Ge(BinaryExpression):
    def __init__(self, a, b):
        BinaryExpression.__init__(self, 'Ge', a, b)

class Lt(BinaryExpression):
    def __init__(self, a, b):
        BinaryExpression.__init__(self, 'Lt', a, b)

class Gt(BinaryExpression):
    def __init__(self, a, b):
        BinaryExpression.__init__(self, 'Gt', a, b)

class BAnd(BinaryExpression):
    def __init__(self, a, b):
        BinaryExpression.__init__(self, 'BAnd', a, b)

class BOr(BinaryExpression):
    def __init__(self, a, b):
        BinaryExpression.__init__(self, 'BOr', a, b)

class BXor(BinaryExpression):
    def __init__(self, a, b):
        BinaryExpression.__init__(self, 'BXor', a, b)

class RShift(BinaryExpression):
    def __init__(self, a, b):
        BinaryExpression.__init__(self, 'Rshift', a, b)

class LShift(BinaryExpression):
    def __init__(self, a, b):
        BinaryExpression.__init__(self, 'Lshift', a, b)


class Sin(UnaryExpression):
    def __init__(self, a):
        UnaryExpression.__init__(self, 'Sin', a)

class Cos(UnaryExpression):
    def __init__(self, a):
        UnaryExpression.__init__(self, 'Cos', a)

class Tan(UnaryExpression):
    def __init__(self, a):
        UnaryExpression.__init__(self, 'Tan', a)

class Cot(UnaryExpression):
    def __init__(self, a):
        UnaryExpression.__init__(self, 'Cot', a)

class Sqrt(UnaryExpression):
    def __init__(self, a):
        UnaryExpression.__init__(self, 'Sqrt', a)

class Sqrt(UnaryExpression):
    def __init__(self, a):
        UnaryExpression.__init__(self, 'Sqrt', a)

class Floor(UnaryExpression):
    def __init__(self, a):
        UnaryExpression.__init__(self, 'Floor', a)

class Ceil(UnaryExpression):
    def __init__(self, a):
        UnaryExpression.__init__(self, 'Ceil', a)




"""
Type Expressions
"""
class Type(TypeExpression, TypeTemplateExpression):
    def __repr__(self):
        return f"Type({self.name})"

class ArrayType(TypeExpression):
    def __init__(self, t, c):
        if not((istype(t, TypeExpression) or istype(t, Expression)) and istype(c, Const)):
            raise GrammarTreeError()
        TypeExpression.__init__(self, 'ArrayType', t, c)

class RefType(TypeExpression):
    def __init__(self, *type_expressions):
        TypeExpression.__init__(self, 'RefType', *type_expressions)

class RecType(TypeExpression):
    def __init__(self, *type_init_statements):
        for s in type_init_statements:
            if not(istype(s, InitWithType)):
                raise GrammarTreeError()
        TypeExpression.__init__(self, 'RecType', *type_init_statements)

class TypeFunctorType(TypeExpression):
    def __init__(self, name, *type_expressions):
        for e in type_expressions:
            if not(istype(e, TypeExpression) or istype(e, Expression)):
                raise GrammarTreeError()
        TypeExpression.__init__(self, name, *type_expressions)



class AssignType(Statement):
    def __init__(self, t_var, type_expression):
        if not(istype(t_var, TypeTemplateExpression) and istype(type_expression, TypeExpression)):
            raise GrammarTreeError()
        Statement.__init__(self, 'AssignType', t_var, type_expression)

class TypeTemplate(TypeTemplateExpression):
    def __init__(self, t_var_name, *t_vars):
        if not(istype(t_var_name, Type)):
            raise GrammarTreeError()
        for t_var in t_vars:
            if not(istype(t_var, Type)):
                raise GrammarTreeError()

        TypeTemplateExpression.__init__(self, 'TypeTemplate', t_var_name, *t_vars)


class AssignTypeList(Element):
    def __init__(self, *assign_types):
        for assign_type in assign_types:
            if not istype(assign_type, AssignType):
                raise GrammarTreeError()
        Element.__init__(self, 'AssignTypeList', *assign_types)
