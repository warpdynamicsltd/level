import level.core.compiler
import level.core.ast as ast
from level.core.compiler.types import Type, TypeVar

class TypeDef:
    def __init__(self, compiler, t, type_vars, type_def):
        self.compiler = compiler
        self.t = t
        self.type_vars = type_vars
        self.type_def = type_def
        self.T = None

    def substitute_statement(self, statement, substitute):
        args = []
        for i in range(len(statement.args)):
            e = statement.args[i]
            if type(e) is ast.Type:
                key = e.name

                v = TypeVar(key)
                if v in substitute:
                    s = substitute[v]
                    if type(s) is TypeVar:
                        e = ast.Type(substitute[v].name)
                    else:
                        e = ast.Type(substitute[v])
            else:
                self.substitute_statement(e, substitute)
            args.append(e)

        statement.args = args

    def compile(self, from_subroutine_header, with_type_var, types=[]):
        if not self.type_vars and self.T is not None:
            return self.T

        substitute = {}
        for i, t in enumerate(types):
            substitute[self.type_vars[i]] = t

        type_def = self.type_def.clone()

        self.substitute_statement(type_def, substitute)

        T = self.compiler.compile_type_expression(type_def, from_subroutine_header=from_subroutine_header, with_type_var=with_type_var)
        T.user_name = self.t.name
        self.T = T
        return T



class TypeDefs:
    def __init__(self):
        self.type_defs = {}

    def add(self, type_def):
        self.type_defs[type_def.t.name] = type_def

    def get_type_def(self, t, types=[]):
        if t.name not in self.type_defs:
            return None
            # raise level.core.compiler.CompilerException(f"can't resolve type '{t.name}' in {t.meta}")

        return self.type_defs[t.name]

    def get_type(self, from_subroutine_header, with_type_var, t, types=[]):
        type_def = self.get_type_def(t, types)

        if type_def is None:
            if from_subroutine_header:
                with_type_var.add(True)
                return TypeVar(t.name)
            else:
                raise level.core.compiler.CompilerException(f"can't resolve type '{t.name}' in {t.meta}")

        return type_def.compile(from_subroutine_header, with_type_var=with_type_var, types=types)


