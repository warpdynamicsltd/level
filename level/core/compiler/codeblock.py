class CodeBlockContext:
    def __init__(self, compiler, obj_manager):
        self.compiler = compiler
        self.obj_manager = obj_manager
        self.objs = []

    def add_obj(self, obj):
        self.objs.append(obj)

    def compile_mass_del(self):
        for obj in self.objs:
            if not obj.returned:
                self.compiler.call_special_subroutine(self.obj_manager, True, "del", obj)

class CodeBlockContexts:
    def __init__(self, compiler):
        self.code_block_contexts = []
        self.compiler = compiler

    def open_new(self, obj_manager):
        self.code_block_contexts.append(CodeBlockContext(self.compiler, obj_manager))

    def compile_current_mass_del(self):
        self.code_block_contexts[-1].compile_mass_del()

    def close_current(self):
        self.code_block_contexts.pop()

    def add_obj(self, obj):
        self.code_block_contexts[-1].add_obj(obj)

