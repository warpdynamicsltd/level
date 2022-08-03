from level.core.compiler.types import Obj, Type
from level.core.compiler.x86_64.types.u32 import U32
from level.core.compiler.x86_64.types.ref import Ref
from level.core.x86_64 import *

class Rec(Obj):
    size = None
    def __init__(self, object_manager, T, ptr=None, for_child_manager=False, value=None, referenced=False):
        self.object_manager = object_manager
        self.length = 1
        self.type = T
        #print(T, T.size())
        if ptr is None:
            self.ptr = object_manager.reserve_variable_ptr(self.type.size(), for_child_manager)
        else:
            self.ptr = ptr
        self.referenced = referenced

        self.index_map = dict()
        self.type_map = dict()
        self.init_map = dict()

        s = 0
        for i, t in enumerate(self.type.sub_types):
            name, value = self.type.meta_data[i]
            self.index_map[name] = s
            self.type_map[name] = t
            self.init_map[name] = value
            if value is not None:
                self.MC_get_from_storage(r14)
                add_(r14, s)
                t.main_type(self.object_manager, ptr=r14, value=value, T=T, referenced=False)

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
        self.MC_get_from_storage(rdi)
        obj.MC_get_from_storage(rsi)
        mov_(ecx, self.type.size())
        loop = address()
        mov_(al, [rsi + ecx - 1])
        mov_([rdi + ecx - 1], al)
        dec_(ecx)
        jnz_(loop)

    def to_acc(self):
        self.MC_get_from_storage(r15)
        lea_(rax, [r15])

    def set_by_acc(self):
        obj = self.type.main_type(object_manager=None, T=self.type, ptr=rax)
        self.set(obj)

