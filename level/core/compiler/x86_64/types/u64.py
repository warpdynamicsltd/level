from level.core.compiler.types import Obj, Type
from level.core.compiler.x86_64.types.bool import Bool
from level.core.x86_64 import *

class U64(Obj):
    size = 8
    priority = 16

    @classmethod
    def int2reg(cls, i, reg):
        if type(i) is int:
            mov_(reg, i)
        else:
            i.MC_get_from_storage(reg)

    def __init__(self,
                 object_manager,
                 value=None,
                 ptr=None,
                 for_child_manager=False,
                 T=None,
                 referenced=False):
        #self.size = 4
        if T is None:
            self.type = Type(U64)
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

    def set_by_acc(self):
        self.MC_put_to_storage(rax)

    def to_acc(self):
        self.MC_get_from_storage(rax)

    def __add__(self, other):
        res = U64(self.object_manager, value=None)
        U64.int2reg(other, rcx)

        self.MC_get_from_storage(rax)
        add_(rax, rcx)
        res.MC_put_to_storage(rax)
        return res

    def __sub__(self, other):
        res = U64(self.object_manager, value=None)
        U64.int2reg(other, rcx)
        self.MC_get_from_storage(rax)
        sub_(rax, rcx)
        res.MC_put_to_storage(rax)
        return res

    def __mul__(self, other):
        res = U64(self.object_manager, value=None)
        U64.int2reg(other, rcx)
        self.MC_get_from_storage(rax)
        mul_(rcx)
        res.MC_put_to_storage(rax)
        return res

    def  __rsub__(self, other):
        res = U64(self.object_manager, value=None)
        U64.int2reg(other, rcx)
        self.MC_get_from_storage(rax)
        sub_(rcx, rax)
        res.MC_put_to_storage(rax)
        return res

    def __radd__(self, other):
        return self.__add__(other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def add(self, other):
        U64.int2reg(other, rcx)
        self.MC_get_from_storage(rax)
        add_(rax, rcx)
        self.MC_put_to_storage(rax)

    def inc(self):
        self.MC_get_from_storage(rax)
        inc_(rax)
        self.MC_put_to_storage(rax)

    def dec(self):
        self.MC_get_from_storage(rax)
        dec_(rax)
        self.MC_put_to_storage(rax)

    def mul(self, other):
        U64.int2reg(other, rcx)
        self.MC_get_from_storage(rax)
        mul_(rcx)
        self.MC_put_to_storage(rax)

    def __iadd__(self, other):
        self.add(other)
        return self

    def __floordiv__(self, other):
        res = U64(self.object_manager, value=None)
        self.MC_get_from_storage(rax)
        U64.int2reg(other, rcx)
        xor_(rdx, rdx)
        div_(rcx)
        res.MC_put_to_storage(rax)
        return res

    def __rfloordiv__(self, other):
        res = U64(self.object_manager, value=None)
        self.MC_get_from_storage(rcx)
        U64.int2reg(other, rax)
        xor_(rdx, rdx)
        div_(rcx)
        res.MC_put_to_storage(rax)
        return res

    def __mod__(self, other):
        res = U64(self.object_manager, value=None)
        self.MC_get_from_storage(rax)
        U64.int2reg(other, rcx)
        xor_(rdx, rdx)
        div_(rcx)
        res.MC_put_to_storage(rdx)
        return res

    def __rmod__(self, other):
        res = U64(self.object_manager, value=None)
        self.MC_get_from_storage(rcx)
        U64.int2reg(other, rax)
        xor_(rdx, rdx)
        div_(rcx)
        res.MC_put_to_storage(rdx)
        return res

    def __eq__(self, other):
        res = Bool(self.object_manager, value=None)
        self.MC_get_from_storage(rax)
        U64.int2reg(other, rcx)
        xor_(rax, rcx)
        setz_(al)
        res.MC_put_to_storage(al)
        return res

    def __ne__(self, other):
        res = Bool(self.object_manager, value=None)
        self.MC_get_from_storage(rax)
        U64.int2reg(other, rcx)
        xor_(rax, rcx)
        setnz_(al)
        res.MC_put_to_storage(al)
        return res

    def __lt__(self, other):
        res = Bool(self.object_manager, value=None)
        U64.int2reg(other, rdx)
        self.MC_get_from_storage(rcx)
        xor_(rax, rax)
        cmp_(rcx, rdx)
        setb_(al)
        res.MC_put_to_storage(al)
        return res

    def __gt__(self, other):
        res = Bool(self.object_manager, value=None)
        U64.int2reg(other, rdx)
        self.MC_get_from_storage(rcx)
        xor_(rax, rax)
        cmp_(rcx, rdx)
        seta_(al)
        res.MC_put_to_storage(al)
        return res

    def __le__(self, other):
        res = Bool(self.object_manager, value=None)
        U64.int2reg(other, rdx)
        self.MC_get_from_storage(rcx)
        xor_(rax, rax)
        cmp_(rcx, rdx)
        setbe_(al)
        res.MC_put_to_storage(al)
        return res

    def __ge__(self, other):
        res = Bool(self.object_manager, value=None)
        U64.int2reg(other, rdx)
        self.MC_get_from_storage(rcx)
        xor_(rax, rax)
        cmp_(rcx, rdx)
        setae_(al)
        res.MC_put_to_storage(al)
        return res

    def __imatmul__(self, other):
        U64.int2reg(other, rax)
        self.MC_put_to_storage(rax)
        return self

    def __neg__(self):
        res = U64(self.object_manager, value=None)
        self.MC_get_from_storage(rax)
        neg_(rax)
        res.MC_put_to_storage(rax)
        return res

    def __pos__(self):
        return self

    def set_from_const(self, value):
        mov_(rax, int(value))
        self.MC_put_to_storage(rax)

    def set(self, v):
        v.MC_get_from_storage(rax)
        self.MC_put_to_storage(rax)

    def cast(self, T):
        res = self.object_manager.reserve_variable(T)
        res.set(self)
        return res