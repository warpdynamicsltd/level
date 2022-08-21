import copy as COPY
import level.core.ast as ast
from level.core.compiler.types import Obj, Type
from level.core.compiler.x86_64.types.u32 import U32
from level.core.compiler.x86_64.types.ref import Ref
from level.core.x86_64 import *
from level.core.compiler import CompilerNotLocatedException
class Rec(Obj):
    size = None
    def __init__(self, object_manager, T, ptr=None, for_child_manager=False, value=None, referenced=False, copy=False):
        self.object_manager = object_manager
        self.length = 1
        self.type = T
        self.objs = []
        if ptr is None:
            for i, t in enumerate(self.type.sub_types):
                init_expression = self.type.meta_data[i]
                if type(init_expression) is ast.Const:
                    const = init_expression.name
                else:
                    const = None

                if not copy:
                    obj = object_manager.reserve_variable(t, value=const, for_child_manager=for_child_manager)
                else:
                    obj = object_manager.reserve_variable(t, value=None, for_child_manager=for_child_manager, copy=copy)
                self.objs.append(obj)
            self.ptr = self.objs[0].ptr

        else:
            self.ptr = ptr

        self.referenced = referenced

        self.index_map = dict()
        self.type_map = dict()

        s = 0
        for i, t in enumerate(self.type.sub_types):
            name = self.type.sub_names[i]
            self.index_map[name] = s
            self.type_map[name] = t
            s += t.size()


    def MC_get_from_storage(self, reg):
        if self.referenced:
            mov_(reg, [self.ptr])
        else:
            lea_(reg, [self.ptr])

    def MC_put_to_storage(self, reg):
        if self.referenced:
            mov_([self.ptr], reg)
        else:
            raise Exception('You should be here')
            mov_(self.ptr, reg)

    def init(self):
        for i, t in enumerate(self.type.sub_types):
            init_expression = self.type.meta_data[i]
            init_obj, const = self.object_manager.compiler.compile_init(init_expression, self.object_manager)

            if self.objs[i].type.main_type is Rec:
                self.objs[i].init()

            if init_obj is not None:
                self.objs[i].set(init_obj)

    def get_element(self, name : str):
        index = self.index_map[name]
        # print(index)
        T = self.type_map[name]
        self.MC_get_from_storage(rax)
        add_(rax, index)
        ref = Ref(object_manager=self.object_manager, T=Type(Ref, sub_types=[T]))
        ref.MC_put_to_storage(rax)
        obj = T.main_type(self.object_manager, ptr=ref.ptr, T=T, referenced=True)
        return obj

    def set(self, obj):
        if obj.type.main_type in {Rec, Ref}:
            self.MC_get_from_storage(rdi)
            obj.MC_get_from_storage(rsi)
            mov_(ecx, self.type.size())
            loop = address()
            mov_(al, [rsi + ecx - 1])
            mov_([rdi + ecx - 1], al)
            dec_(ecx)
            jnz_(loop)
        else:
            raise CompilerNotLocatedException(f"no cast from {obj.type} to {self.type}")

    def to_acc(self):
        self.MC_get_from_storage(r15)
        lea_(rax, [r15])

    def set_by_acc(self):
        obj = self.type.main_type(object_manager=None, T=self.type, ptr=rax)
        self.set(obj)

