from level.core.x86_64 import *
import level.core.ast as ast
from copy import copy

class Global:
    def __init__(self,
                 definition,
                 compiler,
                 ):
        self.definition = definition
        self.compiler = compiler
        var = ast.MetaVar()
        type_expression = ast.MetaVar()
        init_expression = ast.MetaVar()
        ast.InitGlobalWithType(var, type_expression, init_expression) << self.definition
        compiler.var_name_raise_not_available(var.val)
        if type(type_expression.val) is ast.TypeVoid:
            self.T = compiler.compile_driver.get_type_by_const(init_expression.val)
        else:
            self.T = compiler.compile_type_expression(type_expression.val)

        self.calling_name = var.val.calling_name

        if type(init_expression.val) is ast.Const or type(init_expression.val) is ast.ConstVoid:
            self.const = init_expression.val.name
            self.init_expression = None
        else:
            self.const = None
            self.init_expression = init_expression.val

    def compile(self, obj_manager):
        obj_manager.reserve_variable_ptr(size=1)
        obj_manager.reserve_variable_by_name(self.T, self.calling_name, self.const)


class Globals:
    def __init__(self,
                 compiler):

        self.compiler = compiler
        self.obj_manager = self.compiler.obj_manager_type(compiler)
        self.globals_dict = {}
        self.address = SymBits(bits=64)

    def set_data_address(self):
        set_symbol(self.address)
        add_bytes(bytes(self.obj_manager.cursor))

    def add(self, g):
        self.globals_dict[g.calling_name] = g

    def init(self, obj_manager):
        for key in self.globals_dict:
            g = self.globals_dict[key]
            if g.init_expression is not None:
                self.get_obj(key, obj_manager)

    def compile(self):
        if len(self.globals_dict) == 0:
            return
        mov_(rbp, self.address)
        for key in self.globals_dict:
            g = self.globals_dict[key]
            g.compile(self.obj_manager)

    def get_obj(self, key, obj_manager):
        if key not in self.obj_manager.objs:
            return None
        obj = self.obj_manager.objs[key]
        g = self.globals_dict[key]
        obj.ptr = copy(obj.ptr)
        obj.ptr.reg = ESI
        obj.ptr.optimise(False)
        mov_(rsi, self.address)
        ref_T = self.compiler.compile_driver.get_ref_type_for_obj(obj)
        ref_obj = obj_manager.reserve_variable(ref_T)
        ref_obj.bind(obj)
        res = ref_obj.get_obj()
        res.ptr.optimise(False)

        if g.init_expression is not None:
            jmp_addr = self.compiler.compile_driver.compile_global_init_begin(self.address + (obj.index - 1))
            init_obj = self.compiler.compile_expression(g.init_expression, obj_manager)
            self.compiler.compile_assigment(obj_manager, res, init_obj)
            self.compiler.compile_driver.compile_global_init_end(jmp_addr)

        return res
