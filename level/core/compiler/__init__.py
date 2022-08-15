from abc import ABC, abstractmethod

from collections import defaultdict

import level.core.ast as ast
#from level.core.compiler import CallAddress
from level.core.compiler.subroutines import Subroutine, Subroutines, CallAddress, Template, Templates
from level.core.compiler.type_defs import TypeDefs, TypeDef
from level.core.compiler.globals import Globals, Global
from level.core.compiler.types import Obj, Type, TypeVar
from level.core.parser.builtin import translate_simple_types


class CompilerException(Exception):
    pass

class CompilerNotLocatedException(Exception):
    pass

class CompileDriver(ABC):
    @abstractmethod
    def begin(self):
        pass

    @abstractmethod
    def end(self):
        pass

    @abstractmethod
    def get_current_address(self):
        return None

    @abstractmethod
    def call(self, addr : CallAddress):
        pass

    @abstractmethod
    def ret(self):
        pass

    @abstractmethod
    def get_type_by_const(self, c):
        pass

    @abstractmethod
    def get_array_type_by_const(self, c):
        pass

    @abstractmethod
    def get_type_by_var(self, c):
        pass

    @abstractmethod
    def get_type_by_call_address(self, addr : CallAddress):
        pass

    @abstractmethod
    def echo_obj(self, obj):
        pass

    @abstractmethod
    def add_compiler_data(self):
        pass

    @abstractmethod
    def echo_acc_handle(self):
        pass

    @abstractmethod
    def ifelse_acc(self, else_=False):
        pass

    @abstractmethod
    def while_acc(self):
        pass

    @abstractmethod
    def exit(self):
        pass

    @abstractmethod
    def operator(self, op_T, obj1, obj2):
        pass

class ObjManager(ABC):
    def __init__(self, compile_driver : CompileDriver):
        self.objs = {}
        self.compile_driver = compile_driver

    @abstractmethod
    def set_main_frame(self):
        pass

    @abstractmethod
    def reserve_variable(self, T):
        return None

    @abstractmethod
    def create_child_obj_manager(self):
        return None

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def reserve_variable_for_child_obj_manager(self, T, handle):
        pass

    def reserve_variable_by_name(self, T, name, value=None, copy=False):
        if name in self.objs:
            return False
        self.objs[name] = self.reserve_variable(T, value, copy=copy)
        return True

class Compiler:
    def __init__(self, program : ast.Program, obj_manager_type: type, compile_driver_type: type, memory: int=0x100000):
        self.program = program
        self.compile_driver = compile_driver_type()
        self.obj_manager_type = obj_manager_type
        self.subroutines = Subroutines()
        self.templates = Templates()
        self.calling_keys = set()
        self.type_defs = TypeDefs()
        self.globals = Globals(self)
        self.main_program = False
        self.memory = memory

        self.meta = None

        # for internal cache use
        self.subroutines_compiled = set()
        self.type_defs_compiled = {}

    def update_meta(self, exp):
        if exp is not None and exp.meta is not None:
            self.meta = exp.meta

    def compile(self):
        self.compile_driver.begin()

        types = ast.MetaVar()
        global_inits = ast.MetaVar()
        defs = ast.MetaVar()
        statements = ast.MetaVar()

        ast.Program(types, global_inits, defs, statements) << self.program

        self.compile_types(types.val)

        self.compile_def_headers(defs.val)

        self.compile_global_inits(global_inits.val)
        self.globals.compile()

        self.main_program = True

        object_manager = self.obj_manager_type(self.compile_driver, memory=self.memory)
        object_manager.set_main_frame()

        self.compile_statements(statements.val, obj_manager=object_manager)
        self.compile_driver.end()

        self.main_program = False

        self.compile_subroutines()

        self.compile_driver.add_compiler_data()
        self.globals.set_data_address()

        object_manager.close()

    def compile_types(self, types_block):
        for arg in types_block.args:
            self.update_meta(arg)
            template_var = ast.MetaVar()
            type_expression = ast.MetaVar()
            ast.AssignType(template_var, type_expression) << arg

            type_vars = []
            for v in template_var.val.args[1:]:
                type_vars.append(TypeVar(v.name))

            self.type_defs.add(
                TypeDef(
                    compiler=self,
                    t=template_var.val.args[0],
                    type_vars=type_vars,
                    type_def=type_expression.val))

    def compile_global_inits(self, global_inits):
        for g_init_def in global_inits.args:
            self.globals.add(Global(g_init_def, self))

    def compile_def_headers(self, defs):
        for d in defs.args:
            self.compile_def_header(d)

    def compile_subroutines(self):
        while self.subroutines.subroutines_stack:
            subroutine = self.subroutines.subroutines_stack.pop()
            subroutine.compile()

    def compile_def_header(self, d):
        self.update_meta(d)
        """
        This function doesn't generate any machine code
        """
        name = ast.MetaVar()
        var_list = ast.MetaVar()
        statement_list = ast.MetaVar()
        return_type = ast.MetaVar()
        ast.SubroutineDef(name, var_list, statement_list, return_type) << d

        return_type_computed = self.compile_type_expression(return_type.val, from_subroutine_header=True)

        fun_name = name.val

        if fun_name in self.type_defs.type_defs:
            raise CompilerException(f"global name '{fun_name}' can't be used as subroutine name in {d.meta}")

        self.calling_keys.add(fun_name)

        address = self.compile_driver.get_current_address()

        var_types = []
        var_inits = []
        var_names = []

        template = False
        first_default = None
        for i, v in enumerate(var_list.val.args):
            self.update_meta(v)
            var = ast.MetaVar()
            type_expression = ast.MetaVar()
            const = ast.MetaVar()
            with_type_var = set()
            if ast.istype(v, ast.InitWithType):
                ast.InitWithType(var, type_expression, const) << v

                # if there is no init value const.val is None
                if type(type_expression.val) is ast.TypeVoid:
                    T = self.compile_driver.get_type_by_const(const.val)
                else:
                    T = self.compile_type_expression(type_expression.val, from_subroutine_header=True, with_type_var=with_type_var)

                if with_type_var:
                    template = True

                if first_default is None and type(const.val) is not ast.ConstVoid:
                    first_default = i

                if type(const.val) is not ast.ConstVoid and with_type_var:
                    raise CompilerException(f"template vars not allowed with default values in {type_expression.val.meta}")

                if first_default is not None and i > first_default and type(const.val) is ast.ConstVoid:
                    raise CompilerException(f"default value required in {var.val.meta}")

                var_types.append(T)
                var_inits.append(const.val)
                var_names.append(var.val.name)
            else:
                type_expression.val = v
                T = self.compile_type_expression(type_expression.val, from_subroutine_header=True, with_type_var=with_type_var)
                if with_type_var:
                    template = True
                var_types.append(T)
                var_inits.append(None)
                var_names.append(None)


        if not template:
            if self.subroutines.exists(fun_name, var_types):
                return None

            subroutine = self.subroutines.add(key=fun_name, sub=Subroutine(
                                                                compiler=self,
                                                                name=name.val,
                                                                var_types=var_types,
                                                                first_default=first_default,
                                                                var_inits=var_inits,
                                                                var_names=var_names,
                                                                address=address,
                                                                return_type=return_type_computed,
                                                                statement_list=statement_list.val,
                                                                meta=d.meta))

            return subroutine
        else:
            if self.templates.exists(fun_name, var_types):
                return None

            template = self.templates.add(key=fun_name, template=Template(
                                                                    compiler=self,
                                                                    name=name.val,
                                                                    var_types=var_types,
                                                                    first_default=first_default,
                                                                    var_inits=var_inits,
                                                                    var_names=var_names,
                                                                    #return_type=return_type.val,
                                                                    return_type=return_type_computed,
                                                                    statement_list=statement_list.val,
                                                                    meta=d.meta))

            return template

    def compile_statements(self, statements, obj_manager):
        for s in statements.args:
            self.compile_statement(s, obj_manager)

    def var_name_raise_not_available(self, var_exp):
        name = var_exp.name
        calling_name = var_exp.calling_name
        if \
                calling_name in self.calling_keys or \
                name in translate_simple_types or \
                calling_name in self.type_defs.type_defs or \
                calling_name in self.globals.globals_dict:
            raise CompilerException(f"global name '{name}' can't be used as variable name in {var_exp.meta}")

    def compile_statement(self, s, obj_manager):
        self.update_meta(s)

        if ast.istype(s, ast.InitWithType):
            var = ast.MetaVar()
            type_expression = ast.MetaVar()
            const = ast.MetaVar()
            ast.InitWithType(var, type_expression, const) << s
            self.var_name_raise_not_available(var.val)
            if type(type_expression.val) is ast.TypeVoid:
                T = self.compile_driver.get_type_by_const(const.val)
            else:
                T = self.compile_type_expression(type_expression.val)
            if not obj_manager.reserve_variable_by_name(T, var.val.name, const.val.name):
                raise CompilerException(f"variable name '{var.val.name}' already used in this scope, can't initiate in {var.val.meta}")
            return

        if ast.istype(s, ast.Identify):
            var = ast.MetaVar()
            expression = ast.MetaVar()
            ast.Identify(var, expression) << s
            obj = self.compile_expression(expression.val, obj_manager)
            obj_manager.objs[var.val.name] = obj
            return

        if ast.istype(s, ast.Assign):
            var_exp = ast.MetaVar()
            exp = ast.MetaVar()

            ast.Assign(var_exp, exp) << s

            obj = self.compile_expression(exp.val, obj_manager)

            if type(var_exp.val) is ast.Var:
                if not (var_exp.val.name in obj_manager.objs or var_exp.val.calling_name in self.globals.globals_dict):
                    self.var_name_raise_not_available(var_exp.val)
                    obj_manager.reserve_variable_by_name(obj.type, var_exp.val.name)

            var_obj = self.compile_expression(var_exp.val, obj_manager)

            var_obj.set(obj)
            return

        if ast.istype(s, ast.Echo):
            exp = ast.MetaVar()
            ast.Echo(exp) << s
            obj = self.compile_expression(exp.val, obj_manager)
            self.compile_driver.echo_obj(obj)
            return

        if ast.istype(s, ast.Return):
            if s.args:
                obj = self.compile_expression(s.args[0], obj_manager)
                obj.to_acc()

            if self.main_program:
                self.compile_driver.exit()
            else:
                self.compile_driver.ret()

            return

        if ast.istype(s, ast.Exec):
            exp = ast.MetaVar()
            ast.Return(exp) << s
            self.compile_expression(exp.val, obj_manager)
            return

        if ast.istype(s, ast.Inc):
            expression = ast.MetaVar()
            ast.Inc(expression) << s
            obj = self.compile_expression(expression.val, obj_manager)
            obj.inc()
            return

        if ast.istype(s, ast.Dec):
            expression = ast.MetaVar()
            ast.Inc(expression) << s
            obj = self.compile_expression(expression.val, obj_manager)
            obj.dec()
            return

        if ast.istype(s, ast.IfElse):
            condition = ast.MetaVar()
            if_statements = ast.MetaVar()
            else_statements = ast.MetaVar()
            ast.IfElse(condition, if_statements, else_statements) << s
            obj = self.compile_expression(condition.val, obj_manager)
            obj.to_acc()
            gen = self.compile_driver.ifelse_acc(else_=True if else_statements.val.args else False)
            next(gen)
            self.compile_statements(if_statements.val, obj_manager)
            next(gen)
            if else_statements.val.args:
                self.compile_statements(else_statements.val, obj_manager)
                next(gen)
            return

        if ast.istype(s, ast.While):
            condition = ast.MetaVar()
            statements = ast.MetaVar()
            ast.While(condition, statements) << s
            gen = self.compile_driver.while_acc()
            next(gen)
            obj = self.compile_expression(condition.val, obj_manager)
            obj.to_acc()
            next(gen)
            self.compile_statements(statements.val, obj_manager)
            next(gen)
            return

        if ast.istype(s, ast.Break):
            self.compile_driver.compile_break()
            return

        if ast.istype(s, ast.For):
            init_statement = ast.MetaVar()
            condition_expression = ast.MetaVar()
            final_statement = ast.MetaVar()
            for_statement_list = ast.MetaVar()
            ast.For(init_statement, condition_expression, final_statement, for_statement_list) << s
            self.compile_statement(init_statement.val, obj_manager)
            gen = self.compile_driver.while_acc()
            next(gen)
            obj = self.compile_expression(condition_expression.val, obj_manager)
            obj.to_acc()
            next(gen)
            self.compile_statements(for_statement_list.val, obj_manager)
            self.compile_statement(final_statement.val, obj_manager)
            next(gen)
            return

        if ast.istype(s, ast.ForEach):
            init_var_or_expression = ast.MetaVar()
            iteration_expression = ast.MetaVar()
            statement_list = ast.MetaVar()
            ast.ForEach(init_var_or_expression, iteration_expression, statement_list) << s

            if ast.istype(init_var_or_expression.val, ast.Expression):
                exp = init_var_or_expression.val
                obj = self.compile_expression(exp, obj_manager)
            elif ast.istype(init_var_or_expression.val, ast.InitWithType):
                var_name = init_var_or_expression.val.args[0].name
                self.compile_statement(init_var_or_expression.val, obj_manager)
                obj = obj_manager.objs[var_name]
            else:
                raise CompilerException(f"badly formed foreach statement in {s.meta}")

            iteration_obj = self.compile_expression(iteration_expression.val, obj_manager)
            iterator_method = self.get_defined_for_call(True, iteration_expression.val.meta, 'iterator', iteration_obj)
            iterator_obj = self.compile_call_execution(True, obj_manager, iterator_method, iteration_obj)
            ref = self.compile_driver.build_ref(obj_manager, obj)
            next_method = self.get_defined_for_call(True, iteration_expression.val.meta, 'next', iterator_obj, ref)
            gen = self.compile_driver.while_acc()
            next(gen)
            bool_obj = self.compile_call_execution(True, obj_manager, next_method, iterator_obj, ref)
            bool_obj.to_acc()
            next(gen)
            self.compile_statements(statement_list.val, obj_manager)
            next(gen)
            return

        if ast.istype(s, ast.EmptyStatement):
            return

        raise CompilerException(f"wrong statement type: {type(s)}")

    def compile_object_call(self, calling_meta, obj_manager, obj, *exps):
        objs = []
        for exp in exps:
            objs.append(self.compile_expression(exp, obj_manager))

        subroutine = self.get_defined_for_call(True, calling_meta, '()', obj, *objs)
        if subroutine is not None:
            return self.compile_call_execution(True, obj_manager, subroutine, obj, *objs)

        return obj(*objs)

    def compile_expression(self, exp, obj_manager):
        self.update_meta(exp)

        if ast.istype(exp, ast.Call):

            if ast.istype(exp.args[0], ast.Var):
                calling_name = exp.args[0].calling_name
                name = exp.args[0].name
                if calling_name in self.calling_keys:
                    return self.compile_call(ast.SubroutineCall(exp.calling_name, *exp.args[1:]).add_meta(exp.meta), obj_manager)
                elif name in translate_simple_types:
                    T = self.compile_type_expression(ast.Type(name))
                    return self.compile_object_call(exp.meta, obj_manager, T, *exp.args[1:])
                elif name == 'array':
                    return self.compile_type_expression(ast.ArrayType(*exp.args[1:]))
                else:
                    d = self.type_defs.get_type_def(ast.TypeFunctor(calling_name))
                    if d is not None and len(d.type_vars) == 0:
                        T = self.compile_type_expression(ast.Type(name).add_calling_name(calling_name))
                        return self.compile_object_call(exp.meta, obj_manager, T)
                    return self.compile_type_expression(ast.TypeFunctor(calling_name, *exp.args[1:]).add_meta(exp.meta))

            if ast.istype(exp.args[0], ast.ValueAtName):
                expression = ast.MetaVar()
                const = ast.MetaVar()
                ast.ValueAtName(expression, const) << exp.args[0]
                return self.compile_call(ast.SubroutineCall(const.val.name, expression.val, *exp.args[1:]).add_meta(exp.meta), obj_manager, method=True)

            obj = self.compile_expression(exp.args[0], obj_manager)
            return self.compile_object_call(exp.meta, obj_manager, obj, *exp.args[1:])

        if ast.istype(exp, ast.ApiCall):
            name_var = exp.args[0]
            objs = []
            for arg in exp.args[1:]:
                objs.append(self.compile_expression(arg, obj_manager))

            return getattr(self.compile_driver, f"compile_api_{name_var.name}")(obj_manager, *objs)

        if ast.istype(exp, ast.Ref):
            expression = ast.MetaVar()
            ast.Ref(expression) << exp
            obj = self.compile_expression(expression.val, obj_manager)
            if isinstance(obj, Obj):
                T = self.compile_driver.get_ref_type_for_obj(obj)
                ref = obj_manager.reserve_variable(T)
                self.compile_driver.bind(ref, obj)
                return ref
            else:
                T = obj
                return self.compile_driver.get_ref_type_for_type(T)


        if ast.istype(exp, ast.Val):
            expression = ast.MetaVar()
            ast.Val(expression) << exp
            ref = self.compile_expression(expression.val, obj_manager)
            return self.compile_driver.deref(ref)

        if ast.istype(exp, ast.Const):
            T = self.compile_driver.get_type_by_const(exp)
            obj = obj_manager.reserve_variable(T, exp.name)
            return obj

        if ast.istype(exp, ast.Var):
            if exp.calling_name in self.globals.globals_dict:
                return self.globals.get_obj(exp.calling_name, obj_manager)

            if obj_manager is None or not(exp.name in obj_manager.objs):
                if exp.name in translate_simple_types:
                    calling_name = exp.name
                else:
                    calling_name = exp.calling_name
                T = self.compile_type_expression(ast.Type(calling_name).add_meta(exp.meta))
                return T

            return obj_manager.objs[exp.name]

        if ast.istype(exp, ast.ValueAt):
            expression = exp.args[0]
            index_expressions = exp.args[1:]
            obj = self.compile_expression(expression, obj_manager)

            index_objs = []
            for index_expression in index_expressions:
                index_objs.append(self.compile_expression(index_expression, obj_manager))

            subroutine = self.get_defined_for_call(True, exp.meta, '[]', obj, *index_objs)
            if subroutine is not None:
                return self.compile_call_execution(True, obj_manager, subroutine, obj, *index_objs)

            if len(index_expressions) >= 1:
                return obj.get_element(index_objs[0])

            raise CompilerException(f"not defined [] in {exp.meta}")

        if ast.istype(exp, ast.ValueAtName):
            expression = ast.MetaVar()
            const = ast.MetaVar()
            ast.ValueAtName(expression, const) << exp
            obj = self.compile_expression(expression.val, obj_manager)
            if obj.type.main_type.__name__ == 'Ref':
                obj = self.compile_driver.deref(obj)

            return obj.get_element(const.val.name)

        if ast.istype(exp, ast.BinaryExpression):
            return self.compile_binary(exp, exp.args[0], exp.args[1], obj_manager)

        if ast.istype(exp, ast.UnaryExpression):
            return self.compile_unary(exp, exp.args[0], obj_manager)

        raise CompilerException(f"wrong expression type: {str(exp)} in {exp.meta}")


    def compile_binary(self, op_exp, exp1, exp2, obj_manager):
        op_T = type(op_exp)
        obj1 = self.compile_expression(exp1, obj_manager)
        obj2 = self.compile_expression(exp2, obj_manager)

        subroutine = self.get_defined_for_call(True, op_exp.meta, op_exp.raw_str, obj1, obj2)
        if subroutine is not None:
            return self.compile_call_execution(True, obj_manager, subroutine, obj1, obj2)

        res = self.compile_driver.operator(op_T, obj1, obj2)
        return res

    def compile_unary(self, op_exp, exp, obj_manager):
        op_T = type(op_exp)
        if ast.istype(exp, ast.TypeExpression):
            obj = self.compile_type_expression(exp)
        else:
            obj = self.compile_expression(exp, obj_manager)

        subroutine = self.get_defined_for_call(True, op_exp.meta, op_exp.raw_str, obj)
        if subroutine is not None:
            return self.compile_call_execution(True, obj_manager, subroutine, obj)


        res = self.compile_driver.unary_operator(op_T, obj, obj_manager)
        return res

    def compile_call_execution(self, method, obj_manager, subroutine, *objs):
        i = -1
        first_T = None
        for i, obj in enumerate(objs):
            if type(obj) is Type:
                continue
            if (method and i == 0 and obj.type.main_type.__name__ != 'Ref') or (obj.type == first_T):
                first_T = obj.type
                ref = self.compile_driver.build_ref(obj_manager, obj)
                obj_manager.reserve_variable_for_child_obj_manager(ref.type, ref)
            else:
                obj_manager.reserve_variable_for_child_obj_manager(obj.type, obj)

        for k in range(i + 1, len(subroutine.var_types)):
            T = subroutine.var_types[k]
            value = subroutine.var_inits[k].name
            obj_manager.reserve_variable_for_child_obj_manager(T, None, value)

        child_obj_manager = obj_manager.create_child_obj_manager()
        self.compile_driver.call(subroutine.address)
        child_obj_manager.close()
        T = subroutine.return_type
        obj = obj_manager.reserve_variable(T, copy=True)
        obj.set_by_acc()

        self.subroutines.subroutines_stack.append(subroutine)
        return obj

    def get_defined_for_call(self, method, calling_meta, fun_key, *objs):
        var_types = []
        first_T = None
        for i, obj in enumerate(objs):
            if type(obj) is Type:
                T = obj
            else:
                if (method and i == 0 and obj.type.main_type.__name__ != 'Ref') or (obj.type == first_T):
                    first_T = obj.type
                    T = self.compile_driver.get_ref_type_for_obj(obj)
                else:
                    T = obj.type

            var_types.append(T)

        sub = self.subroutines.get(calling_meta, fun_key, var_types)
        if sub is None:
            sub = self.templates.get_subroutine(calling_meta, fun_key, var_types)

        return sub

    def compile_call(self, sub, obj_manager, method=False):
        self.update_meta(sub)

        objs = []
        for i, exp in enumerate(sub.args):
            if ast.istype(exp, ast.Expression):
                objs.append(self.compile_expression(exp, obj_manager))
            if ast.istype(exp, ast.TypeExpression):
                T = self.compile_type_expression(exp)
                objs.append(T)

        subroutine = self.get_defined_for_call(method, sub.meta, sub.name, *objs)

        if subroutine is None:
            raise CompilerException(f"can't resolve subroutine name '{sub.name}' in {sub.meta}")

        return self.compile_call_execution(method, obj_manager, subroutine, *objs)


    def compile_type_expression(self, s, from_subroutine_header=False, with_type_var=set()):
        self.update_meta(s)

        if ast.istype(s, ast.Type):
            # when subroutine is created from template, unknown types are substituted with internal computed types
            if type(s.name) is Type:
                return s.name

            res = self.compile_driver.get_simple_type_by_name(s)
            if res is not None:
                return res
            else:
                return self.type_defs.get_type(from_subroutine_header=from_subroutine_header, with_type_var=with_type_var, t=s)

        if ast.istype(s, ast.ArrayType):
            type_expression = ast.MetaVar()
            const = ast.MetaVar()
            ast.ArrayType(type_expression, const) << s
            exp = type_expression.val
            if ast.istype(exp, ast.TypeExpression):
                T = self.compile_type_expression(exp, from_subroutine_header=from_subroutine_header,
                                                 with_type_var=with_type_var)
            else:
                T = self.compile_expression(exp, None)
            n = int(const.val.name)
            return Type(main_type=self.compile_driver.get_array_type(), length=n, sub_types=[T])

        if ast.istype(s, ast.RefType):
            sub_types = []
            if s.args:
                sub_types.append(self.compile_type_expression(s.args[0], from_subroutine_header=from_subroutine_header, with_type_var=with_type_var))
            return Type(main_type=self.compile_driver.get_ref_type(), sub_types=sub_types)

        if ast.istype(s, ast.RecType):
            names = []
            types = []
            for arg in s.args:
                var = ast.MetaVar()
                type_expression = ast.MetaVar()
                const = ast.MetaVar()
                ast.InitWithType(var, type_expression, const) << arg
                if type(type_expression.val) is ast.TypeVoid:
                    T = self.compile_driver.get_type_by_const(const.val)
                else:
                    T = self.compile_type_expression(type_expression.val, from_subroutine_header=from_subroutine_header, with_type_var=with_type_var)
                names.append((var.val.name, const.val.name))
                types.append(T)
            return Type(main_type=self.compile_driver.get_rec_type(), sub_types=types, meta_data=names)

        if ast.istype(s, ast.TypeFunctor):
            Ts = []
            for exp in s.args:
                if ast.istype(exp, ast.TypeExpression):
                    T = self.compile_type_expression(exp, from_subroutine_header=from_subroutine_header,
                                             with_type_var=with_type_var)
                else:
                    T = self.compile_expression(exp, None)

                if not(type(T) is Type or type(T) is TypeVar):
                    raise CompilerException(f"type expected in {exp.meta}")

                Ts.append(T)
            return self.type_defs.get_type(from_subroutine_header=from_subroutine_header, with_type_var=with_type_var,
                                           t=s, types=Ts)