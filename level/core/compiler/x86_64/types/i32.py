from level.core.compiler.types import Obj, Type
from level.core.compiler.x86_64.types.bool import Bool
from level.core.x86_64 import *

class I32(Obj):
    size = 4
    priority = 5

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
                 referenced=False,
                 copy=False):
        #self.size = 4
        if T is None:
            self.type = Type(I32)
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

        if reg.bits > 32:
            mov_(r15, 0xffffffff)
            and_(rax, r15)

    def MC_put_to_storage(self, reg):
        if reg.bits > 32:
            reg = Register(reg=reg.reg, bits=32)

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
        res = I32(self.object_manager, value=None)
        I32.int2reg(other, ecx)

        self.MC_get_from_storage(eax)
        add_(eax, ecx)
        res.MC_put_to_storage(eax)
        return res

    def __sub__(self, other):
        res = I32(self.object_manager, value=None)
        I32.int2reg(other, ecx)
        self.MC_get_from_storage(eax)
        sub_(eax, ecx)
        res.MC_put_to_storage(eax)
        return res

    def __mul__(self, other):
        res = I32(self.object_manager, value=None)
        I32.int2reg(other, ecx)
        self.MC_get_from_storage(eax)
        imul_(ecx)
        res.MC_put_to_storage(eax)
        return res

    def  __rsub__(self, other):
        res = I32(self.object_manager, value=None)
        I32.int2reg(other, ecx)
        self.MC_get_from_storage(eax)
        sub_(ecx, eax)
        res.MC_put_to_storage(eax)
        return res

    def __radd__(self, other):
        return self.__add__(other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def add(self, other):
        I32.int2reg(other, ecx)
        self.MC_get_from_storage(eax)
        add_(eax, ecx)
        self.MC_put_to_storage(eax)

    def inc(self):
        self.MC_get_from_storage(eax)
        inc_(eax)
        self.MC_put_to_storage(eax)

    def dec(self):
        self.MC_get_from_storage(eax)
        dec_(eax)
        self.MC_put_to_storage(eax)

    def mul(self, other):
        I32.int2reg(other, ecx)
        self.MC_get_from_storage(eax)
        imul_(ecx)
        self.MC_put_to_storage(eax)

    def __iadd__(self, other):
        self.add(other)
        return self

    def __floordiv__(self, other):
        res = I32(self.object_manager, value=None)
        self.MC_get_from_storage(eax)
        I32.int2reg(other, ecx)
        mov_(ebx, 1)
        neg_(ebx)
        xor_(edx, edx)
        or_(eax, eax)
        cmovs_(edx, ebx)
        idiv_(ecx)
        res.MC_put_to_storage(eax)
        return res

    def __rfloordiv__(self, other):
        res = I32(self.object_manager, value=None)
        self.MC_get_from_storage(ecx)
        I32.int2reg(other, eax)
        mov_(ebx, 1)
        neg_(ebx)
        xor_(edx, edx)
        or_(eax, eax)
        cmovs_(edx, ebx)
        idiv_(ecx)
        res.MC_put_to_storage(eax)
        return res

    def __mod__(self, other):
        res = I32(self.object_manager, value=None)
        self.MC_get_from_storage(eax)
        I32.int2reg(other, ecx)
        mov_(ebx, 1)
        neg_(ebx)
        xor_(edx, edx)
        or_(eax, eax)
        cmovs_(edx, ebx)
        idiv_(ecx)
        res.MC_put_to_storage(edx)
        return res

    def __rmod__(self, other):
        res = I32(self.object_manager, value=None)
        self.MC_get_from_storage(ecx)
        I32.int2reg(other, eax)
        mov_(ebx, 1)
        neg_(ebx)
        xor_(edx, edx)
        or_(eax, eax)
        cmovs_(edx, ebx)
        div_(ecx)
        res.MC_put_to_storage(edx)
        return res

    def __eq__(self, other):
        res = Bool(self.object_manager, value=None)
        self.MC_get_from_storage(eax)
        I32.int2reg(other, ecx)
        xor_(eax, ecx)
        setz_(al)
        res.MC_put_to_storage(al)
        return res

    def __ne__(self, other):
        res = Bool(self.object_manager, value=None)
        self.MC_get_from_storage(eax)
        I32.int2reg(other, ecx)
        xor_(eax, ecx)
        setnz_(al)
        res.MC_put_to_storage(al)
        return res

    def __lt__(self, other):
        res = Bool(self.object_manager, value=None)
        I32.int2reg(other, edx)
        self.MC_get_from_storage(ecx)
        xor_(eax, eax)
        cmp_(ecx, edx)
        setl_(al)
        res.MC_put_to_storage(al)
        return res

    def __gt__(self, other):
        res = Bool(self.object_manager, value=None)
        I32.int2reg(other, edx)
        self.MC_get_from_storage(ecx)
        xor_(eax, eax)
        cmp_(ecx, edx)
        setg_(al)
        res.MC_put_to_storage(al)
        return res

    def __le__(self, other):
        res = Bool(self.object_manager, value=None)
        I32.int2reg(other, edx)
        self.MC_get_from_storage(ecx)
        xor_(eax, eax)
        cmp_(ecx, edx)
        setle_(al)
        res.MC_put_to_storage(al)
        return res

    def __ge__(self, other):
        res = Bool(self.object_manager, value=None)
        I32.int2reg(other, edx)
        self.MC_get_from_storage(ecx)
        xor_(eax, eax)
        cmp_(ecx, edx)
        setge_(al)
        res.MC_put_to_storage(al)
        return res

    def __imatmul__(self, other):
        I32.int2reg(other, eax)
        self.MC_put_to_storage(eax)
        return self

    def __neg__(self):
        res = I32(self.object_manager, value=None)
        self.MC_get_from_storage(eax)
        neg_(eax)
        res.MC_put_to_storage(eax)
        return res
    
    def __invert__(self):
        res = I32(self.object_manager, value=None)
        self.MC_get_from_storage(eax)
        not_(eax)
        res.MC_put_to_storage(eax)
        return res

    def __and__(self, other):
        res = I32(self.object_manager, value=None)
        I32.int2reg(other, ecx)
        self.MC_get_from_storage(eax)
        and_(eax, ecx)
        res.MC_put_to_storage(eax)
        return res

    def __or__(self, other):
        res = I32(self.object_manager, value=None)
        I32.int2reg(other, ecx)
        self.MC_get_from_storage(eax)
        or_(eax, ecx)
        res.MC_put_to_storage(eax)
        return res

    def __xor__(self, other):
        res = I32(self.object_manager, value=None)
        I32.int2reg(other, ecx)
        self.MC_get_from_storage(eax)
        xor_(eax, ecx)
        res.MC_put_to_storage(eax)
        return res

    def __rshift__(self, other):
        res = I32(self.object_manager, value=None)
        I32.int2reg(other, ecx)
        self.MC_get_from_storage(eax)
        sar_(eax, cl)
        res.MC_put_to_storage(eax)
        return res

    def __lshift__(self, other):
        res = I32(self.object_manager, value=None)
        I32.int2reg(other, ecx)
        self.MC_get_from_storage(eax)
        sal_(eax, cl)
        res.MC_put_to_storage(eax)
        return res

    def __pos__(self):
        return self

    def __abs__(self):
        res = I32(self.object_manager, value=None)
        self.MC_get_from_storage(eax)
        mov_(ecx, eax)
        neg_(eax)
        cmovl_(eax, ecx)
        res.MC_put_to_storage(eax)
        return res

    def sgn(self):
        res = I32(self.object_manager, value=None)
        self.MC_get_from_storage(rax)
        mov_(ebx, 1)
        mov_(ecx, 1)
        neg_(ecx)
        or_(eax, eax)
        cmovs_(eax, ecx)
        cmovg_(eax, ebx)
        res.MC_put_to_storage(eax)
        return res

    def set_from_const(self, value):
        mov_(eax, value)
        self.MC_put_to_storage(eax)

    def cast_and_store(self, v):
        pass

    def set(self, v):
        v.MC_get_from_storage(rax)
        self.cast_and_store(v)
        self.MC_put_to_storage(rax)
