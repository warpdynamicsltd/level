import sys

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
                 var_types,
                 first_default,
                 var_inits,
                 var_names,
                 address : CallAddress,
                 return_type: Type,
                 statement_list,
                 meta):
        self.compiler = compiler
        self.name = name
        self.address = address
        self.var_types = var_types
        self.first_default = first_default
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
            if name is not None:
                obj_manager.reserve_variable_by_name(self.var_types[i], name, copy=True)

        for s in self.statement_list.args:
            self.compiler.compile_statement(s, obj_manager)

        self.compiler.compile_driver.ret()
        obj_manager.close()
        self.compiled = True

    def match(self, var_types):
        if not self.var_types:
        # we want functions without arguments to be checked at the end if there is no other candidates
            return False

        if len(var_types) < len(self.var_types[:self.first_default]):
            return False
        limit = len(var_types)
        return var_types == self.var_types[:limit]

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

    def get(self, calling_meta, key, var_types):
        if key not in self.subroutines:
            return None

        matches = []
        no_args_matches = []
        for sub in self.subroutines[key]:
            if sub.match(var_types):
                matches.append(sub)

            if not sub.var_types:
                no_args_matches.append(sub)

        if len(matches) > 1:
            msg = ""
            for sub in matches:
                msg += f"matched function {sub.name.key} in {sub.meta}\n"
            raise level.core.compiler.CompilerException(f"{msg}ambiguous function call '{key}' in {calling_meta}")

        if len(matches) == 1:
            return matches[0]

        if len(no_args_matches) > 1:
            msg = ""
            for sub in no_args_matches:
                msg += f"matched function {sub.name.key} in {sub.meta}\n"
            raise level.core.compiler.CompilerException(f"{msg}ambiguous function call '{key}' in {calling_meta}")
        # if it hasn't found var type match return no var type if exists

        if len(no_args_matches) == 1:
            return no_args_matches[0]

        return None


class Template:
    def __init__(self,
                 compiler,
                 name,
                 var_types,
                 first_default,
                 var_inits,
                 var_names,
                 return_type : Type,
                 statement_list,
                 meta):
        self.compiler = compiler
        self.name = name
        self.var_types = var_types
        self.first_default = first_default
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

                v = TypeVar(key)
                if v in substitute:
                    e = ast.Type(substitute[v])
            else:
                self.substitute_statement(e, substitute)
            args.append(e)

        statement.args = args

    def create_subroutine(self, meta, var_types, substitute=None):
        if substitute is None:
            substitute = self.general_matcher.match(self.var_types, var_types)

        if substitute is None:
            raise level.core.compiler.CompilerException(f"can't resolve template {self.name.key} defined in {self.meta} called from {meta}")

        substituted_statement_list = []

        for s in self.statement_list.args:
            s_clone = s.clone()
            self.substitute_statement(s_clone, substitute)
            substituted_statement_list.append(s_clone)

        return_type = self.return_type
        for var in substitute:
            try:
                return_type = var.substitute(return_type, substitute[var])
            except TypeVarException:
                raise level.core.compiler.CompilerException(f"can't resolve template {self.name.key} defined in {self.meta} called from {meta}")

        address = self.compiler.compile_driver.get_current_address()


        return Subroutine(
                        compiler=self.compiler,
                        name=self.name,

                        # when there are default parameters in the final positions of arguments they might not take part in arguments query
                        # but they can never contain type variable
                        # thus we can easily add the reminder of var types to var_types
                        var_types=var_types + self.var_types[len(var_types):],
                        first_default=self.first_default,
                        var_inits=self.var_inits,
                        var_names=self.var_names,
                        address=address,
                        return_type=return_type,
                        statement_list=ast.StatementList(*substituted_statement_list),
                        meta=self.meta)

    def match(self, var_types):
        if not self.var_types:
        # we want functions without arguments to be checked at the end if there is no other candidates
            return None

        if len(var_types) < len(self.var_types[:self.first_default]):
            return None
        limit = len(var_types)
        return self.general_matcher.match(self.var_types[:limit], var_types)

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

    def get(self, calling_meta, key, var_types):
        if key not in self.templates:
            return None

        matches = []
        for template in self.templates[key]:
            substitute = template.match(var_types)
            if substitute is not None:
                matches.append((template, substitute))

        if len(matches) > 1:
            msg = ""
            for template, _ in matches:
                msg += f"matched function {template.name.key} in {template.meta}\n"
            raise level.core.compiler.CompilerException(f"{msg}ambiguous function call '{key}' in {calling_meta}")

        if len(matches) == 1:
            return matches[0]

        return None

    def get_subroutine(self, calling_meta, key, var_types):
        res = self.get(calling_meta, key, var_types)

        if res is None:
            return None
        template, substitute = res

        return template.create_subroutine(calling_meta, var_types, substitute)
