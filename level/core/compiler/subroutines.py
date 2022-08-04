from collections import defaultdict
from level.core.compiler.types import Type, TypeVar
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
                 statement_list: list):
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

    def get(self, key, var_types):
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
            raise CompilerException(f"ambiguous function call '{key}'")

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
                 statement_list):
        self.compiler = compiler
        self.name = name
        self.var_types = var_types
        self.var_inits = var_inits
        self.return_type = return_type
        self.statement_list = statement_list
        self.var_names = var_names

    def substitute_statement(self, statement, substitute):
        args = []
        for i in range(len(statement.args)):
            e = statement.args[i]
            if type(e) is ast.Type:
                key = e.name
                if key in substitute:
                    # at this moment usual type name is replaced by internal Type object
                    e = ast.Type(substitute[key])
            else:
                self.substitute_statement(e, substitute)
            args.append(e)

        statement.args = args

    def create_subroutine(self, var_types):
        substitute = {}
        for i, t in enumerate(self.var_types):
            if type(t) is TypeVar:
                substitute[t.name] = var_types[i]

        substituted_statement_list = []

        for s in self.statement_list.args:
            s_clone = s.clone()
            self.substitute_statement(s_clone, substitute)
            substituted_statement_list.append(s_clone)

        address = self.compiler.compile_driver.get_current_address()

        return Subroutine(
                        compiler=self.compiler,
                        name=self.name,
                        var_types=var_types,
                        var_inits=self.var_inits,
                        var_names=self.var_names,
                        address=address,
                        return_type=self.return_type,
                        statement_list=ast.StatementList(*substituted_statement_list))

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

    def get(self, key, var_types):
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
                    res.append(type(template.var_types[i]) is TypeVar or T == template.var_types[i])

                for k in template.var_inits[j:]:
                    # print(k)
                    res.append(k.name is not None)

                if res and len(res) == len(template.var_types) and all(res):
                    matches.append(template)

            if not template.var_types:
                sub_var_no_type = template

        if len(matches) > 1:
            raise CompilerException(f"ambiguous function call '{key}'")

        if len(matches) == 1:
            return matches[0]
        # if it hasn't found var type match return no var type if exists
        return sub_var_no_type

    def get_subroutine(self, key, var_types):
        template = self.get(key, var_types)
        if template is None:
            return None

        return template.create_subroutine(var_types)