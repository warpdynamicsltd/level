from collections import defaultdict

from level.core.compiler.types import Type, TypeVar, TypeVarException
from level.mathtools.matcher import GeneralMatcher
import level.core.compiler
import level.core.ast as ast

class CallAddress():
    def __init__(self, value):
        self.value = value

class Subroutine:
    def __init__(self,
                 compiler,
                 name,
                 var_types : list,
                 var_inits : list,
                 var_names : list,
                 address : CallAddress,
                 return_type: Type,
                 statement_list: list,
                 meta):
        self.compiler = compiler
        self.name = name
        self.address = address
        self.var_types = var_types
        self.var_inits = var_inits
        self.return_type = return_type
        self.statement_list = statement_list
        self.var_names = var_names
        self.used = False
        self.compiled = False
        self.meta = meta

    def use(self):
        self.used = True

    def compile(self):
        if self.compiled:
            return

        obj_manager = self.compiler.obj_manager_type(self.compiler.compile_driver)

        self.compiler.compile_driver.set_call_address(self.address)

        for i, name in enumerate(self.var_names):
            obj_manager.reserve_variable_by_name(self.var_types[i], name)

        for s in self.statement_list.args:
            self.compiler.compile_statement(s, obj_manager)

        self.compiler.compile_driver.ret()
        obj_manager.close()
        self.compiled = True

class Subroutines:
    def __init__(self):
        self.subroutines = defaultdict(list)
        self.subroutines_stack = []

    def add(self, key, sub):
        self.subroutines[key].append(sub)
        return sub

    def exists(self, key, var_types):
        if key in self.subroutines:
            for sub in self.subroutines[key]:
                if sub.var_types == var_types:
                    return True

        return False

    def get(self, meta, key, var_types):
        if key not in self.subroutines:
            return None

        matches = []
        sub_var_no_type = None
        for sub in self.subroutines[key]:
            if len(sub.var_types) >= len(var_types):
                res = []
                j = 0
                for i, T in enumerate(var_types):
                    # print(T)
                    j += 1
                    res.append(T == sub.var_types[i])

                for k in sub.var_inits[j:]:
                    # print(k)
                    res.append(k.name is not None)

                if res and len(res) == len(sub.var_types) and all(res):
                    matches.append(sub)

            if not sub.var_types:
                sub_var_no_type = sub

        if len(matches) > 1:
            raise level.core.compiler.CompilerException(f"ambiguous function call '{key}' in {meta}")

        if len(matches) == 1:
            return matches[0]
        # if it hasn't found var type match return no var type if exists
        return sub_var_no_type


class Template:
    def __init__(self,
                 compiler,
                 name,
                 var_types,
                 var_inits,
                 var_names,
                 return_type,
                 statement_list,
                 meta):
        self.compiler = compiler
        self.name = name
        self.var_types = var_types
        self.var_inits = var_inits
        self.return_type = return_type
        self.statement_list = statement_list
        self.var_names = var_names
        self.general_matcher = GeneralMatcher(TypeVar)
        self.meta = meta

    def substitute_statement(self, statement, substitute):
        args = []
        for i in range(len(statement.args)):
            e = statement.args[i]
            if type(e) is ast.Type:
                key = e.name
                #v = TypeVar(key)
                if key in substitute:
                    # at this moment unknown type name is replaced by internal Type object
                    e = ast.Type(substitute[key])
            else:
                self.substitute_statement(e, substitute)
            args.append(e)

        statement.args = args

    def create_subroutine(self, meta, var_types):
        # print(list(map(str, self.var_types)))
        _substitute = self.general_matcher.match(self.var_types, var_types)
        if _substitute is None:
            raise level.core.compiler.CompilerException(f"can't resolve template {self.name.key} defined in {self.meta} called from {meta}")
        # print(_substitute)
        substitute = {}
        for v in _substitute:
            substitute[v.name] = _substitute[v]

        substituted_statement_list = []

        for s in self.statement_list.args:
            s_clone = s.clone()
            self.substitute_statement(s_clone, substitute)
            substituted_statement_list.append(s_clone)

        # return_type = self.return_type.clone()
        # self.substitute_statement(return_type, substitute)

        #print(return_type)
        return_type = self.return_type
        for var in _substitute:
            try:
                return_type = var.substitute(return_type, _substitute[var])
            except TypeVarException:
                raise level.core.compiler.CompilerException(f"can't resolve template {self.name.key} defined in {self.meta} called from {meta}")

        #print(_substitute)
        # if return_type.sub_types:
        #     print(type(return_type.sub_types[0]))
        # print(str(return_type))

        address = self.compiler.compile_driver.get_current_address()

        return Subroutine(
                        compiler=self.compiler,
                        name=self.name,
                        var_types=var_types,
                        var_inits=self.var_inits,
                        var_names=self.var_names,
                        address=address,
                        return_type=return_type,
                        statement_list=ast.StatementList(*substituted_statement_list),
                        meta=self.meta)

class Templates:
    def __init__(self):
        self.templates = defaultdict(list)

    def add(self, key, template):
        self.templates[key].append(template)
        return template

    def exists(self, key, var_types):
        if key in self.templates:
            for template in self.templates[key]:
                if template.var_types == var_types:
                    return True

        return False

    def get(self, meta, key, var_types):
        if key not in self.templates:
            return None

        matches = []
        sub_var_no_type = None
        for template in self.templates[key]:
            if len(template.var_types) >= len(var_types):
                res = []
                j = 0
                for i, T in enumerate(var_types):
                    # print(T)
                    j += 1
                    #res.append(type(template.var_types[i]) is TypeVar or (T == template.var_types[i]))
                    #res.append(type(template.var_types[i]) is TypeVar or (template.general_matcher.match(template.var_types[i], T) is not None))
                    res.append(template.general_matcher.match(template.var_types[i], T) is not None)

                for k in template.var_inits[j:]:
                    # print(k)
                    res.append(k.name is not None)

                if res and len(res) == len(template.var_types) and all(res):
                    matches.append(template)

            if not template.var_types:
                sub_var_no_type = template

        if len(matches) > 1:
            raise level.core.compiler.CompilerException(f"ambiguous function call '{key}' in {meta}")

        if len(matches) == 1:
            return matches[0]
        # if it hasn't found var type match return no var type if exists
        return sub_var_no_type

    def get_subroutine(self, meta, key, var_types):
        template = self.get(meta, key, var_types)
        if template is None:
            return None

        return template.create_subroutine(meta, var_types)