import level
from level.core.compiler.types import Obj, Type
from level.core.compiler.x86_64.types.u32 import U32
from level.core.compiler.x86_64.types.byte import Byte
from level.core.compiler.x86_64.types.byte import Bool
from level.core.x86_64 import *
from level.core.parser.builtin import BuiltinValue

class Ref(Obj):
    size = 8
    def __init__(self, object_manager, for_child_manager=False, ptr=None, T=None, value=None, referenced=False):
        self.object_manager = object_manager
        self.referenced = referenced

        if T is None:
            self.type = Type(Ref)
        else:
            self.type = T

        if ptr is None:
            self.ptr = object_manager.reserve_variable_ptr(size=self.size, for_child_manager=for_child_manager)
        else:
            self.ptr = ptr

        if value is not None:
            self.set_from_const(value)

    def set_from_const(self, value):
        if type(value) is bytes:
            self.type.sub_types[0].length = len(value)
            addr = SymBits(bits=64)
            mov_(rax, addr)
            self.MC_put_to_storage(rax)
            if self.object_manager is not None:
                self.object_manager.compile_driver.string_table.append(level.core.compiler.x86_64.StringInfo(value, addr))
            return

    def MC_get_from_storage(self, reg):
        if self.referenced:
            mov_(r15, [self.ptr])
            mov_(reg, [r15])
        else:
            mov_(reg, [self.ptr])

    def MC_put_to_storage(self, reg):
        if self.referenced:
            mov_(r15, [self.ptr])
            mov_([r15], reg)
        else:
            mov_([self.ptr], reg)

    def set(self, ref_obj):
        # mov_(rax, [ref_obj.ptr])
        # mov_([self.ptr], rax)
        ref_obj.MC_get_from_storage(rax)
        self.MC_put_to_storage(rax)
        #self.type = ref_obj.type

    def to_acc(self):
        #mov_(rax, [self.ptr])
        self.MC_get_from_storage(rax)

    def set_by_acc(self):
        # mov_([self.ptr], rax)
        self.MC_put_to_storage(rax)

    def bind(self, obj):
        if not obj.referenced:
            lea_(rax, [obj.ptr])
        else:
            mov_(rax, [obj.ptr])

        #mov_([self.ptr], rax)
        self.MC_put_to_storage(rax)
        self.type = Type(main_type=Ref, sub_types=[obj.type])

    def get_obj(self):
        if self.referenced:
            ref = Ref(self.object_manager)
            self.MC_get_from_storage(rax)
            ref.MC_put_to_storage(rax)
            obj = self.type.sub_types[0].main_type(object_manager=self.object_manager, T=self.type.sub_types[0],
                                                   ptr=ref.ptr, referenced=True)
        else:
            obj = self.type.sub_types[0].main_type(object_manager=self.object_manager, T=self.type.sub_types[0], ptr=self.ptr, referenced=True)
        return obj

    def get_element(self, index):
        index.MC_get_from_storage(rax)
        mov_(rcx, self.type.sub_types[0].size())
        mul_(rcx)
        T = self.type.sub_types[0]
        self.MC_get_from_storage(rcx)
        # and_(rax, 0xffffffff)
        add_(rcx, rax)
        ref = Ref(object_manager=self.object_manager, T=Type(Ref, sub_types=[T]))
        ref.MC_put_to_storage(rcx)
        obj = T.main_type(self.object_manager, ptr=ref.ptr, T=T, referenced=True)
        return obj

    def __eq__(self, other):
        res = Bool(self.object_manager, value=None)
        self.MC_get_from_storage(rax)
        other.MC_get_from_storage(rcx)
        xor_(rax, rcx)
        setz_(al)
        res.MC_put_to_storage(al)
        return res

    def __ne__(self, other):
        res = Bool(self.object_manager, value=None)
        self.MC_get_from_storage(rax)
        other.MC_get_from_storage(rcx)
        xor_(rax, rcx)
        setnz_(al)
        res.MC_put_to_storage(al)
        return res

    def cast(self, T):
        res = self.object_manager.reserve_variable(T)
        res.set(self)
        return res