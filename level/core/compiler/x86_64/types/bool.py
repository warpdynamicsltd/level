from level.core.compiler.types import Obj, Type
from level.core.x86_64 import *

class Bool(Obj):
    size = 1
    priority = 0

    def __init__(self,
                 object_manager,
                 value=None,
                 ptr=None,
                 for_child_manager=False,
                 T=None,
                 referenced=False):

        if T is None:
            self.type = Type(Bool)
        else:
            self.type = T

        self.ptr = ptr
        self.value = value
        self.object_manager = object_manager
        self.referenced = referenced
        if ptr is None:
            self.ptr = object_manager.reserve_variable_ptr(self.size, for_child_manager)
        else:
            self.ptr = ptr

        if value is not None:
            # print(value)
            mov_(al, int(value))
            self.MC_put_to_storage(al)

    def MC_get_from_storage(self, reg):
        if reg.bits > 8:
            _reg = Register(reg=reg.reg, bits=8)
        else:
            _reg = reg

        if self.referenced:
            mov_(r15, [self.ptr])
            mov_(_reg, [r15])
        else:
            mov_(_reg, [self.ptr])

        and_(reg, 0x1)

    def MC_put_to_storage(self, reg):
        if reg.bits > 8:
            reg = Register(reg=reg.reg, bits=8)

        if self.referenced:
            mov_(r15, [self.ptr])
            mov_([r15], reg)
        else:
            mov_([self.ptr], reg)

    def set_by_acc(self):
        # mov_([self.ptr], eax)
        self.MC_put_to_storage(al)

    def to_acc(self):
        # mov_(eax, [self.ptr])
        self.MC_get_from_storage(rax)

    def set(self, other):
        other.MC_get_from_storage(rax)
        self.MC_put_to_storage(rax)

    def not_(self):
        res = Bool(self.object_manager, value=None)
        self.MC_get_from_storage(al)
        not_(al)
        res.MC_put_to_storage(al)
        return res

    def and_(self, other):
        res = Bool(self.object_manager, value=None)
        other.MC_get_from_storage(al)
        self.MC_get_from_storage(cl)
        and_(al, cl)
        res.MC_put_to_storage(al)
        return res

    def or_(self, other):
        res = Bool(self.object_manager, value=None)
        other.MC_get_from_storage(al)
        self.MC_get_from_storage(cl)
        or_(al, cl)
        res.MC_put_to_storage(al)
        return res

    def __eq__(self, other):
        res = Bool(self.object_manager, value=None)
        other.MC_get_from_storage(al)
        self.MC_get_from_storage(cl)
        xor_(al, cl)
        setz_(al)
        res.MC_put_to_storage(al)
        return res

    def __ne__(self, other):
        res = Bool(self.object_manager, value=None)
        other.MC_get_from_storage(al)
        self.MC_get_from_storage(cl)
        xor_(al, cl)
        setnz_(al)
        res.MC_put_to_storage(al)
        return res

    def cast(self, T):
        res = self.object_manager.reserve_variable(T)
        res.set(self)
        return res
