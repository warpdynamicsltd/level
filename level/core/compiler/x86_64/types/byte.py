from level.core.compiler.types import Obj, Type
from level.core.compiler.x86_64.types.bool import Bool
from level.core.x86_64 import *

class Byte(Obj):
    size = 1
    priority = 1

    def __init__(self,
                 object_manager,
                 value=None,
                 ptr=None,
                 for_child_manager=False,
                 T=None,
                 referenced=False,
                 copy=False):

        Obj.__init__(self)

        if T is None:
            self.type = Type(Byte)
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
            self.set_from_const(value)

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

        and_(reg, 0xff)

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
        self.MC_get_from_storage(al)

    def set(self, other):
        other.MC_get_from_storage(rax)
        self.MC_put_to_storage(rax)

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
    
    def __invert__(self):
        res = Byte(self.object_manager, value=None)
        self.MC_get_from_storage(al)
        not_(al)
        res.MC_put_to_storage(al)
        return res

    def __and__(self, other):
        res = Byte(self.object_manager, value=None)
        other.MC_get_from_storage(cl)
        self.MC_get_from_storage(al)
        and_(al, cl)
        res.MC_put_to_storage(al)
        return res

    def __or__(self, other):
        res = Byte(self.object_manager, value=None)
        other.MC_get_from_storage(cl)
        self.MC_get_from_storage(al)
        or_(al, cl)
        res.MC_put_to_storage(al)
        return res

    def __xor__(self, other):
        res = Byte(self.object_manager, value=None)
        other.MC_get_from_storage(cl)
        self.MC_get_from_storage(al)
        xor_(al, cl)
        res.MC_put_to_storage(al)
        return res

    def __rshift__(self, other):
        res = Byte(self.object_manager, value=None)
        other.MC_get_from_storage(cl)
        self.MC_get_from_storage(al)
        shr_(al, cl)
        res.MC_put_to_storage(al)
        return res

    def __lshift__(self, other):
        res = Byte(self.object_manager, value=None)
        other.MC_get_from_storage(cl)
        self.MC_get_from_storage(al)
        shl_(al, cl)
        res.MC_put_to_storage(al)
        return res

    def set_from_const(self, value):
        mov_(rax, int(value))
        self.MC_put_to_storage(rax)

    def cast(self, T):
        res = self.object_manager.reserve_variable(T)
        res.set(self)
        return res