from abc import ABC, abstractmethod

from collections import defaultdict

import level.core.ast as ast
from level.core.compiler.types import Type


class CompilerException(Exception):
    pass

class CallAddress():
    def __init__(self, value):
        self.value = value

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

    def reserve_variable_by_name(self, T, name, value=None):
        self.objs[name] = self.reserve_variable(T, value)


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



class Compiler:
    def __init__(self, program : ast.Program, obj_manager_type: type, compile_driver_type: type, memory: int=0x100000):
        self.program = program
        self.compile_driver = compile_driver_type()
        self.obj_manager_type = obj_manager_type
        self.subroutines = Subroutines()
        self.subroutines_route_map = {}
        self.main_program = False
        self.memory = memory

    def compile(self):
        self.compile_driver.begin()

        types = ast.MetaVar()
        defs = ast.MetaVar()
        statements = ast.MetaVar()

        ast.Program(types, defs, statements) << self.program

        self.compile_types(types.val)

        self.compile_def_headers(defs.val)

        self.main_program = True

        object_manager = self.obj_manager_type(self.compile_driver, memory=self.memory)
        object_manager.set_main_frame()

        self.compile_statements(statements.val, obj_manager=object_manager)
        self.compile_driver.end()

        self.main_program = False

        self.compile_subroutines()

        self.compile_driver.add_compiler_data()
        object_manager.close()

    def compile_types(self, types_block):
        for arg in types_block.args:
            t_var = ast.MetaVar()
            type_expression = ast.MetaVar()
            ast.AssignType(t_var, type_expression) << arg
            T = self.compile_type_expression(type_expression.val)
            type_name = t_var.val.name.name
            T.user_name = type_name
            # print(str(T))
            self.compile_driver.set_type_by_name(type_name, T)

    def compile_def_headers(self, defs):
        for d in defs.args:
            self.compile_def_header(d)

    def compile_subroutines(self):
        for key in self.subroutines.subroutines:
            for subroutine in self.subroutines.subroutines[key]:
                subroutine.compile()

    def compile_def_header(self, d):
        """
        This function doesn't generate any machine code
        """
        name = ast.MetaVar()
        var_list = ast.MetaVar()
        statement_list = ast.MetaVar()
        return_type = ast.MetaVar()
        ast.SubroutineDef(name, var_list, statement_list, return_type) << d

        fun_name = name.val.key
        alternative_fun_name = name.val.name

        address = self.compile_driver.get_current_address()

        var_types = []
        var_inits = []
        var_names = []

        for v in var_list.val.args:
            var = ast.MetaVar()
            type_expression = ast.MetaVar()
            const = ast.MetaVar()
            ast.InitWithType(var, type_expression, const) << v

            # if there is no init value const.val is None
            if type(type_expression.val) is ast.TypeVoid:
                T = self.compile_driver.get_type_by_const(const.val)
            else:
                T = self.compile_type_expression(type_expression.val)

            var_types.append(T)
            var_inits.append(const.val)
            var_names.append(var.val.name)

        if self.subroutines.exists(fun_name, var_types):
            return None

        subroutine = self.subroutines.add(key=fun_name, sub=Subroutine(
                                                            compiler=self,
                                                            name=name.val,
                                                            var_types=var_types,
                                                            var_inits=var_inits,
                                                            var_names=var_names,
                                                            address=address,
                                                            return_type=return_type.val,
                                                            statement_list=statement_list.val))

        self.subroutines_route_map[alternative_fun_name] = fun_name

        return subroutine


    def compile_statements(self, statements, obj_manager):
        for s in statements.args:
            self.compile_statement(s, obj_manager)


    def compile_statement(self, s, obj_manager):
        #print(type(s))
        if ast.istype(s, ast.Init):
            var = ast.MetaVar()
            ast.Init(var) << s
            T = self.compile_driver.get_type_by_var(var.val)
            obj_manager.reserve_variable_by_name(T, var.val.name)
            return

        if ast.istype(s, ast.InitWithType):
            var = ast.MetaVar()
            type_expression = ast.MetaVar()
            const = ast.MetaVar()
            ast.InitWithType(var, type_expression, const) << s
            if type(type_expression.val) is ast.TypeVoid:
                T = self.compile_driver.get_type_by_const(const.val)
            else:
                T = self.compile_type_expression(type_expression.val)
            obj_manager.reserve_variable_by_name(T, var.val.name, const.val.name)
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
                if var_exp.val.name not in obj_manager.objs:
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

        if ast.istype(s, ast.EmptyStatement):
            return

        raise CompilerException(f"wrong statement type: {type(s)}")

    def compile_expression(self, exp, obj_manager):
        if ast.istype(exp, ast.Call):
            if ast.istype(exp.args[0], ast.Var):
                return self.compile_call(ast.SubroutineCall(exp.lead.name, *exp.args[1:]).add_meta(exp.meta), obj_manager)

            if ast.istype(exp.args[0], ast.ValueAtName):
                expression = ast.MetaVar()
                const = ast.MetaVar()
                ast.ValueAtName(expression, const) << exp.args[0]
                return self.compile_call(ast.SubroutineCall(const.val.name, expression.val, *exp.args[1:]).add_meta(exp.meta), obj_manager, method=True)

            obj = self.compile_expression(exp.args[0])
            return obj(*exp.args[1:])

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
            T = self.compile_driver.get_ref_type_for_obj(obj)
            ref = obj_manager.reserve_variable(T)
            self.compile_driver.bind(ref, obj)
            return ref

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
            if exp.name not in obj_manager.objs:
                raise CompilerException(f"can't resolve variable '{exp.name}' in {exp.meta}")
            return obj_manager.objs[exp.name]

        if ast.istype(exp, ast.ValueAt):
            expression = exp.args[0]
            index_expressions = exp.args[1:]
            obj = self.compile_expression(expression, obj_manager)

            index_objs = []
            for index_expression in index_expressions:
                index_objs.append(self.compile_expression(index_expression, obj_manager))

            subroutine = self.get_defined_call(True, '[]', obj, *index_objs)
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

        raise CompilerException(f"wrong expression type: {type(exp)}")


    def compile_binary(self, op_exp, exp1, exp2, obj_manager):
        op_T = type(op_exp)
        obj1 = self.compile_expression(exp1, obj_manager)
        obj2 = self.compile_expression(exp2, obj_manager)

        subroutine = self.get_defined_call(True, op_exp.raw_str, obj1, obj2)
        if subroutine is not None:
            return self.compile_call_execution(True, obj_manager, subroutine, obj1, obj2)

        res = self.compile_driver.operator(op_T, obj1, obj2)
        return res

    def compile_unary(self, op_exp, exp, obj_manager):
        op_T = type(op_exp)
        obj = self.compile_expression(exp, obj_manager)

        subroutine = self.get_defined_call(True, op_exp.raw_str, obj)
        if subroutine is not None:
            return self.compile_call_execution(True, obj_manager, subroutine, obj)


        res = self.compile_driver.unary_operator(op_T, obj)
        return res

    def compile_call_execution(self, method, obj_manager, subroutine, *objs):
        i = 0
        first_T = None
        for i, obj in enumerate(objs):
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
        T = self.compile_type_expression(subroutine.return_type)
        obj = obj_manager.reserve_variable(T)
        obj.set_by_acc()
        return obj

    def get_defined_call(self, method, fun_key, *objs):
        var_types = []
        first_T = None
        for i, obj in enumerate(objs):
            if (method and i == 0 and obj.type.main_type.__name__ != 'Ref') or (obj.type == first_T):
                first_T = obj.type
                T = self.compile_driver.get_ref_type_for_obj(obj)
            else:
                T = obj.type

            var_types.append(T)

        return self.subroutines.get(fun_key, var_types)

    def compile_call(self, sub, obj_manager, method=False):
        if sub.name not in self.subroutines_route_map:
            raise CompilerException(f"can't resolve subroutine name '{sub.name}' in {sub.meta}")

        fun_key = self.subroutines_route_map[sub.name]

        objs = []
        for i, exp in enumerate(sub.args):
            objs.append(self.compile_expression(exp, obj_manager))

        subroutine = self.get_defined_call(method, fun_key, *objs)

        if subroutine is None:
            raise CompilerException(f"can't resolve subroutine name '{sub.name}' in {sub.meta}")

        return self.compile_call_execution(method, obj_manager, subroutine, *objs)

    def compile_type_expression(self, s):
        if ast.istype(s, ast.Type):
            return self.compile_driver.get_type_by_name(s)

        if ast.istype(s, ast.ArrayType):
            type_expression = ast.MetaVar()
            const = ast.MetaVar()
            ast.ArrayType(type_expression, const) << s
            T = self.compile_type_expression(type_expression.val)
            n = const.val.name
            return Type(main_type=self.compile_driver.get_array_type(), length=n, sub_types=[T])

        if ast.istype(s, ast.RefType):
            sub_types = []
            if s.args:
                sub_types.append(self.compile_type_expression(s.args[0]))
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
                    T = self.compile_type_expression(type_expression.val)
                names.append((var.val.name, const.val.name))
                types.append(T)
            return Type(main_type=self.compile_driver.get_rec_type(), sub_types=types, meta_data=names)