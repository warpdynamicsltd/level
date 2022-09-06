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
    # used just for stats
    n_compiled = 0

    def __init__(self,
                 compiler,
                 name,
                 direct,
                 var_types,
                 first_default,
                 var_inits,
                 var_names,
                 address : CallAddress,
                 ref_return : bool,
                 return_type: Type,
                 statement_list,
                 meta):
        self.compiler = compiler
        self.name = name
        self.direct = direct
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
        self.ref_return = ref_return
        self.gc_active = False

    def use(self):
        self.used = True

    def create_child_subroutine(self, ancestor_T, original_T, var_types):
        return_type = self.return_type
        if self.return_type == ancestor_T:
            return_type = original_T
        if self.return_type.main_type.__name__ == 'Ref' and self.return_type.sub_types and self.return_type.sub_types[0] == ancestor_T:
            return_type = self.compiler.compile_driver.get_ref_type_for_type(original_T)

        address = self.compiler.compile_driver.get_new_address()

        return Subroutine(
                        compiler=self.compiler,
                        name=self.name,
                        direct=self.direct,
                        var_types=var_types,
                        first_default=self.first_default,
                        var_inits=self.var_inits,
                        var_names=self.var_names,
                        address=address,
                        ref_return=self.ref_return,
                        return_type=return_type,
                        statement_list=self.statement_list,
                        meta=self.meta)


    def compile(self):
        if self.compiled:
            return

        h = hash(tuple(self.var_types))
        if (self.name, h) in self.compiler.subroutine_compiled_addresses:
            self.address.value.set(self.compiler.subroutine_compiled_addresses[self.name, h].value)
            return

        self.compiler.subroutines_stack.append(self)
        obj_manager = self.compiler.obj_manager_type(self.compiler)
        self.compiler.compile_driver.set_call_address(self.address)

        for i, name in enumerate(self.var_names):
            if name is not None:
                obj_manager.reserve_variable_by_name(self.var_types[i], name, copy=True)

        self.compiler.code_block_contexts.open_new(obj_manager)

        # this is suboptimal construction, it compiles unnecessary jump
        # solution: do pre-compilation in which it will be revealed that mem obj is used in subroutine body
        # TO FIX (the easiest way to add pre-compilator is to put compilation on hold but still compile statements for some
        # if not self.direct:
        #     on_opening_addr, no_action_addr = self.compiler.compile_driver.compile_on_opening(self.compiler, obj_manager, self)

        for s in self.statement_list.args:
            self.compiler.compile_statement(s, obj_manager)

        # if not self.direct:
        #     if not self.gc_active:
        #         self.compiler.compile_driver.compile_on_opening_make_inactive(on_opening_addr, no_action_addr)
        #
        #     self.compile_on_closing(obj_manager)


        # because last statement from each subroutine is always ast.Return() this line is no longer needed
        # but it is here as a reminder
        # self.compiler.compile_driver.ret()

        self.compiler.code_block_contexts.close_current()
        self.compiler.subroutines_stack.pop()
        obj_manager.close()
        Subroutine.n_compiled += 1
        self.compiled = True
        self.compiler.subroutine_compiled_addresses[self.name, h] = self.address

    def compile_on_opening(self, obj_manager):
        if self.name not in {"stdlib:sys:context:on_opening", "stdlib:sys:context:on_closing"}:
            self.compiler.call_special_subroutine(obj_manager, False, "stdlib:sys:context:on_opening")
        pass

    def compile_on_closing(self, obj_manager):
        if self.gc_active and self.name not in {"stdlib:sys:context:on_opening", "stdlib:sys:context:on_closing"}:
            self.compiler.call_special_subroutine(obj_manager, False, "stdlib:sys:context:on_closing")
        pass

    def match(self, var_types):
        if len(var_types) < len(self.var_types[:self.first_default]):
            return False
        limit = len(var_types)
        return var_types == self.var_types[:limit]

class Subroutines:
    def __init__(self):
        self.subroutines = defaultdict(list)
        # used to stack all subroutines for compilation
        self.subroutines_stack = []
        self.subroutines_map = {}

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

        h = hash(tuple(var_types))
        if (key, h) in self.subroutines_map:
            return self.subroutines_map[key, h]

        matches = []
        for sub in self.subroutines[key]:
            if sub.match(var_types):
                matches.append(sub)

        if len(matches) > 1:
            msg = ""
            for sub in matches:
                msg += f"matched function {sub.name.key} in {sub.meta}\n"
            raise level.core.compiler.CompilerException(f"{msg}ambiguous function call '{key}' in {calling_meta}")

        if len(matches) == 1:
            res = matches[0]
        else:
            res = None

        self.subroutines_map[key, h] = res
        return res


class Template:
    def __init__(self,
                 compiler,
                 name,
                 direct,
                 var_types,
                 first_default,
                 var_inits,
                 var_names,
                 ref_return,
                 return_type : Type,
                 statement_list,
                 meta):
        self.compiler = compiler
        self.name = name
        self.direct = direct
        self.var_types = var_types
        self.first_default = first_default
        self.var_inits = var_inits
        self.return_type = return_type
        self.statement_list = statement_list
        self.var_names = var_names
        self.general_matcher = GeneralMatcher(TypeVar)
        self.meta = meta
        self.ref_return = ref_return

        self.subroutines_map = {}

    def create_subroutine(self, meta, var_types, substitute=None):
        h = hash(tuple(var_types + self.var_types[len(var_types):]))
        if h in self.subroutines_map:
            return self.subroutines_map[h]

        if substitute is None:
            substitute = Type.match(self.var_types, var_types)

        if substitute is None:
            raise level.core.compiler.CompilerException(f"can't resolve template {self.name.key} defined in {self.meta} called from {meta}")

        substituted_statement_list = []

        for s in self.statement_list.args:
            s_clone = s.clone()
            s_clone = TypeVar.substitute_ast_element(s_clone, substitute)
            substituted_statement_list.append(s_clone)

        substituted_var_inits = []
        for v in self.var_inits:
            if v is not None:
                v_clone = v.clone()
                v_clone = TypeVar.substitute_ast_element(v_clone, substitute)
                substituted_var_inits.append(v_clone)
            else:
                substituted_var_inits.append(None)

        return_type_clone = self.return_type.clone()
        return_type_clone = TypeVar.substitute_ast_element(return_type_clone, substitute)
        with_type_var = set()
        return_type = self.compiler.compile_type_expression(return_type_clone, from_subroutine_header=True, with_type_var=with_type_var)
        if len(with_type_var) > 0:
            raise level.core.compiler.CompilerException(
                f"can't resolve template {self.name} defined in {self.meta} called from {meta}")

        address = self.compiler.compile_driver.get_new_address()


        res = Subroutine(
                        compiler=self.compiler,
                        name=self.name,
                        direct=self.direct,
                        # when there are default parameters in the final positions of arguments they might not take part in arguments query
                        # but they can never contain type variable
                        # thus we can easily add the reminder of var types to var_types
                        var_types=var_types + self.var_types[len(var_types):],
                        first_default=self.first_default,
                        var_inits=substituted_var_inits,
                        var_names=self.var_names,
                        address=address,
                        ref_return=self.ref_return,
                        return_type=return_type,
                        statement_list=ast.StatementList(*substituted_statement_list),
                        meta=self.meta)

        self.subroutines_map[h] = res
        return res

    def match(self, var_types):
        if len(var_types) < len(self.var_types[:self.first_default]):
            return None
        limit = len(var_types)
        return Type.match(self.var_types[:limit], var_types)

class Templates:
    def __init__(self):
        self.templates = defaultdict(list)
        self.subroutines_map = {}
        self.templates_map = {}

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

        h = hash(tuple(var_types))
        if (key, h) in self.templates_map:
            return h, self.templates_map[key, h]

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
            res = matches[0]
        else:
            return None

        self.templates_map[key, h] = h, res
        return h, res

    def get_subroutine(self, calling_meta, key, var_types):
        res = self.get(calling_meta, key, var_types)

        if res is None:
            return None
        #print(res)
        h, (template, substitute) = res
        if (h, key) in self.subroutines_map:
            return self.subroutines_map[h, key]

        res = template.create_subroutine(calling_meta, var_types, substitute)
        self.subroutines_map[h, key] = res
        return res

