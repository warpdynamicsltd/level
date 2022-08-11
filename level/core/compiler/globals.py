from level.core.x86_64 import *
import level.core.ast as ast

class Global:
    def __init__(self,
                 definition,
                 compiler,
                 ):
        self.definition = definition
        self.compiler = compiler
        var = ast.MetaVar()
        type_expression = ast.MetaVar()
        const = ast.MetaVar()
        ast.InitGlobalWithType(var, type_expression, const) << self.definition
        compiler.var_name_raise_not_available(var.val)
        if type(type_expression.val) is ast.TypeVoid:
            self.T = compiler.compile_driver.get_type_by_const(const.val)
        else:
            self.T = compiler.compile_type_expression(type_expression.val)

        self.calling_name = var.val.calling_name
        self.const = const.val.name

    def compile(self, obj_manager):
        obj_manager.reserve_variable_by_name(self.T, self.calling_name, self.const)


class Globals:
    def __init__(self,
                 compiler):

        self.compiler = compiler
        self.obj_manager = self.compiler.obj_manager_type(compiler.compile_driver)
        self.globals_dict = {}
        self.address = SymBits(bits=64)

    def set_data_address(self):
        set_symbol(self.address)
        add_block(self.obj_manager.cursor)

    def add(self, g):
        self.globals_dict[g.calling_name] = g

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
        obj.ptr.reg = ESI
        mov_(rsi, self.address)
        ref_T = self.compiler.compile_driver.get_ref_type_for_obj(obj)
        ref_obj = obj_manager.reserve_variable(ref_T)
        ref_obj.bind(obj)
        return ref_obj.get_obj()
