class CodeBlockContext:
    def __init__(self, compiler, obj_manager, scope_name='main'):
        self.compiler = compiler
        self.obj_manager = obj_manager
        self.opening_cursor = obj_manager.cursor
        self.scope_name = scope_name
        self.objs_to_del = []
        self.objs_to_del_indices = set()
        self.objs_to_finish = []
        self.objs_to_finish_indices = set()
        self.var_initiated_indices = {}

        self.subroutine = None
        if self.compiler.subroutines_stack:
            self.subroutine = self.compiler.subroutines_stack[-1]

    def add_obj_to_del(self, obj):
        if obj.index not in self.objs_to_del_indices:
            self.objs_to_del.append(obj)
            self.objs_to_del_indices.add(obj.index)

    def add_obj_to_finish(self, obj):
        if obj.index not in self.objs_to_finish_indices:
            self.objs_to_finish.append(obj)
            self.objs_to_finish_indices.add(obj.index)

    def add_initiated_var(self, obj):
        self.var_initiated_indices[obj.index] = obj.name

    def compile_mass_del(self):
        for obj in self.objs_to_del:
            self.compiler.call_special_subroutine(self.obj_manager, True, "del", obj)

    def compile_mass_finish(self):
        for obj in self.objs_to_finish:
            self.compiler.call_special_subroutine(self.obj_manager, True, "finish", obj)

    def close(self):
        for index in self.var_initiated_indices:
            name = self.var_initiated_indices[index]
            del self.obj_manager.objs[name]

        self.obj_manager.cursor = self.opening_cursor

class CodeBlockContexts:
    def __init__(self, compiler):
        self.code_block_contexts = []
        self.compiler = compiler


    def open_new(self, obj_manager, scope_name="main"):
        self.code_block_contexts.append(CodeBlockContext(self.compiler, obj_manager=obj_manager, scope_name=scope_name))

    def compile_current_mass_del(self, i=-1):
        self.code_block_contexts[i].compile_mass_del()

    def compile_current_mass_finish(self, i=-1):
        # currently that will do any job only in root scope
        self.code_block_contexts[i].compile_mass_finish()

    def compile_current_closure(self, i=-1):
        self.compile_current_mass_finish(i)
        self.compile_current_mass_del(i)
        pass

    def compile_on_continue(self):
        i = len(self.code_block_contexts) - 1
        while self.code_block_contexts[i].scope_name == 'ifelse':
            self.compile_current_closure(i)
            i-=1
        self.compile_current_closure(i)

    def compile_on_break(self):
        i = len(self.code_block_contexts) - 1
        while self.code_block_contexts[i].scope_name == 'ifelse':
            self.compile_current_closure(i)
            i -= 1
        self.compile_current_closure(i)

    def compile_on_return(self):
        i = len(self.code_block_contexts) - 1
        while i >= 0:
            self.compile_current_closure(i)
            i -= 1

    def close_current(self):
        if self.code_block_contexts:
            self.code_block_contexts[-1].close()
            self.code_block_contexts.pop()

    def add_obj_to_del(self, obj):

        if self.code_block_contexts:
            code_block_context = self.code_block_contexts[-1]
            if code_block_context.subroutine is not None:
                if "metal" in code_block_context.subroutine.modes:
                    return
            code_block_context.add_obj_to_del(obj)

    def add_obj_to_finish(self, obj):
        if self.code_block_contexts:
            # so far we don't support scope local variables, so all variables are initiated in root scope
            # and there they need to be also finished
            # code_block_context = self.code_block_contexts[0]
            code_block_context = self.code_block_contexts[-1]
            if code_block_context.subroutine is not None:
                if "metal" in code_block_context.subroutine.modes:
                    return
            code_block_context.add_obj_to_finish(obj)

    def add_initiated_var(self, obj):
        if self.code_block_contexts:
            self.code_block_contexts[-1].add_initiated_var(obj)



