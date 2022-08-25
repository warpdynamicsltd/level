import level.core.compiler
import level.core.ast as ast
from level.core.compiler.types import Type, TypeVar

class TypeDef:
    # used just for stats
    n_compiled = 0

    def __init__(self, compiler, t, type_vars, parent_type_defs, type_def):
        self.compiler = compiler
        self.t = t
        self.type_vars = type_vars
        self.type_def = type_def
        self.parent_type_defs = parent_type_defs
        self.T = None

    def compile(self, from_subroutine_header, with_type_var, types=[]):
        # print(self.type_def)
        h = hash(tuple(types))
        if (self.t.name, from_subroutine_header, h) in self.compiler.type_defs_compiled:
            wtv, resT = self.compiler.type_defs_compiled[self.t.name, from_subroutine_header, h]
            if wtv:
                with_type_var.add(True)
            return resT

        if not self.type_vars and self.T is not None:
            return self.T

        substitute = {}
        for i, t in enumerate(types):
            substitute[self.type_vars[i]] = t

        type_def = self.type_def.clone()

        parent_types = []
        parent_novar_types = []
        wtv = False
        for parent_type_def in self.parent_type_defs:
            parent_type_def = TypeVar.substitute_ast_element(parent_type_def.clone(), substitute)
            _with_type_var = set()
            t = self.compiler.compile_type_expression(parent_type_def, from_subroutine_header=from_subroutine_header, with_type_var=_with_type_var)
            if _with_type_var:
                wtv = True
            else:
                parent_novar_types.append(t)

            parent_types.append(t)

        type_def = TypeVar.substitute_ast_element(type_def, substitute)
        T = self.compiler.compile_type_expression(type_def, from_subroutine_header=from_subroutine_header,
                                                  with_type_var=with_type_var)


        for t in parent_types:
            T = T + t

        T.user_name = self.t.name
        T.reset_hash()

        if not with_type_var:
            self.compiler.inheritance.map[hash(T)] = T
            for t in parent_novar_types:
                self.compiler.inheritance.add_inheritance(hash(T), hash(t))
                self.compiler.inheritance.map[hash(t)] = t

        self.T = T
        TypeDef.n_compiled += 1
        wtv = (True if len(with_type_var) > 0 else False) or wtv
        if wtv:
            with_type_var.add(True)
        self.compiler.type_defs_compiled[self.t.name, from_subroutine_header, h] = wtv, T
        return T

class TypeDefs:
    def __init__(self):
        self.type_defs = {}

    def add(self, type_def):
        self.type_defs[type_def.t.name] = type_def

    def get_type_def(self, t, types=[]):
        if t.name not in self.type_defs:
            return None

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


