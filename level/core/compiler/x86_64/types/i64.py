from level.core.compiler.types import Obj, Type
from level.core.compiler.x86_64.types.bool import Bool
from level.core.compiler.x86_64.types.i32 import I32
from level.core.compiler.x86_64.types.u32 import U32
from level.core.compiler.x86_64.types.u64 import U64
from level.core.compiler.x86_64.types.float import Float
from level.core.compiler.x86_64.types.ref import Ref
from level.core.compiler.x86_64.types.byte import Byte
from level.core.compiler.x86_64.types.bool import Bool
import level.core.compiler.x86_64.types.float
from level.core.x86_64 import *
from level.core.compiler import CompilerException

class I64(Obj):
    size = 8
    priority = 17

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

        if T is None:
            self.type = Type(I64)
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

    def get_ptr(self):
        if self.referenced:
            mov_(r15, [self.ptr])
            return r15
        else:
            return self.ptr

    def set_by_acc(self):
        self.MC_put_to_storage(rax)

    def to_acc(self):
        self.MC_get_from_storage(rax)

    def __add__(self, other):
        res = I64(self.object_manager, value=None)
        I64.int2reg(other, rcx)

        self.MC_get_from_storage(rax)
        add_(rax, rcx)
        res.MC_put_to_storage(rax)
        return res

    def __sub__(self, other):
        res = I64(self.object_manager, value=None)
        I64.int2reg(other, rcx)
        self.MC_get_from_storage(rax)
        sub_(rax, rcx)
        res.MC_put_to_storage(rax)
        return res

    def __mul__(self, other):
        res = I64(self.object_manager, value=None)
        I64.int2reg(other, rcx)
        self.MC_get_from_storage(rax)
        imul_(rcx)
        res.MC_put_to_storage(rax)
        return res

    def  __rsub__(self, other):
        res = I64(self.object_manager, value=None)
        I64.int2reg(other, rcx)
        self.MC_get_from_storage(rax)
        sub_(rcx, rax)
        res.MC_put_to_storage(rax)
        return res

    def __radd__(self, other):
        return self.__add__(other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def add(self, other):
        I64.int2reg(other, rcx)
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
        I64.int2reg(other, rcx)
        self.MC_get_from_storage(rax)
        imul_(rcx)
        self.MC_put_to_storage(rax)

    def __iadd__(self, other):
        self.add(other)
        return self

    def __floordiv__(self, other):
        res = I64(self.object_manager, value=None)
        self.MC_get_from_storage(rax)
        I64.int2reg(other, rcx)
        mov_(rbx, 1)
        neg_(rbx)
        xor_(rdx, rdx)
        or_(rax, rax)
        cmovs_(rdx, rbx)
        idiv_(rcx)
        res.MC_put_to_storage(rax)
        return res

    def __rfloordiv__(self, other):
        res = I64(self.object_manager, value=None)
        self.MC_get_from_storage(rcx)
        I64.int2reg(other, rax)
        mov_(rbx, 1)
        neg_(rbx)
        xor_(rdx, rdx)
        or_(rax, rax)
        cmovs_(rdx, rbx)
        idiv_(rcx)
        res.MC_put_to_storage(rax)
        return res

    def __mod__(self, other):
        res = I64(self.object_manager, value=None)
        self.MC_get_from_storage(rax)
        I64.int2reg(other, rcx)
        mov_(rbx, 1)
        neg_(rbx)
        xor_(rdx, rdx)
        or_(rax, rax)
        cmovs_(rdx, rbx)
        idiv_(rcx)
        res.MC_put_to_storage(rdx)
        return res

    def __rmod__(self, other):
        res = I64(self.object_manager, value=None)
        self.MC_get_from_storage(rcx)
        I64.int2reg(other, rax)
        mov_(rbx, 1)
        neg_(rbx)
        xor_(rdx, rdx)
        or_(rax, rax)
        cmovs_(rdx, rbx)
        div_(rcx)
        res.MC_put_to_storage(rdx)
        return res

    def __eq__(self, other):
        res = Bool(self.object_manager, value=None)
        self.MC_get_from_storage(rax)
        I64.int2reg(other, rcx)
        xor_(rax, rcx)
        setz_(al)
        res.MC_put_to_storage(al)
        return res

    def __ne__(self, other):
        res = Bool(self.object_manager, value=None)
        self.MC_get_from_storage(rax)
        I64.int2reg(other, rcx)
        xor_(rax, rcx)
        setnz_(al)
        res.MC_put_to_storage(al)
        return res

    def __lt__(self, other):
        res = Bool(self.object_manager, value=None)
        I64.int2reg(other, rdx)
        self.MC_get_from_storage(rcx)
        xor_(rax, rax)
        cmp_(rcx, rdx)
        setl_(al)
        res.MC_put_to_storage(al)
        return res

    def __gt__(self, other):
        res = Bool(self.object_manager, value=None)
        I64.int2reg(other, rdx)
        self.MC_get_from_storage(rcx)
        xor_(rax, rax)
        cmp_(rcx, rdx)
        setg_(al)
        res.MC_put_to_storage(al)
        return res

    def __le__(self, other):
        res = Bool(self.object_manager, value=None)
        I64.int2reg(other, rdx)
        self.MC_get_from_storage(rcx)
        xor_(rax, rax)
        cmp_(rcx, rdx)
        setle_(al)
        res.MC_put_to_storage(al)
        return res

    def __ge__(self, other):
        res = Bool(self.object_manager, value=None)
        I64.int2reg(other, rdx)
        self.MC_get_from_storage(rcx)
        xor_(rax, rax)
        cmp_(rcx, rdx)
        setge_(al)
        res.MC_put_to_storage(al)
        return res

    def __imatmul__(self, other):
        I64.int2reg(other, rax)
        self.MC_put_to_storage(rax)
        return self

    def __neg__(self):
        res = I64(self.object_manager, value=None)
        self.MC_get_from_storage(rax)
        neg_(rax)
        res.MC_put_to_storage(rax)
        return res
    
    def __invert__(self):
        res = I64(self.object_manager, value=None)
        self.MC_get_from_storage(rax)
        not_(rax)
        res.MC_put_to_storage(rax)
        return res

    def __and__(self, other):
        res = I64(self.object_manager, value=None)
        I64.int2reg(other, rcx)
        self.MC_get_from_storage(rax)
        and_(rax, rcx)
        res.MC_put_to_storage(rax)
        return res

    def __or__(self, other):
        res = I64(self.object_manager, value=None)
        I64.int2reg(other, rcx)
        self.MC_get_from_storage(rax)
        or_(rax, rcx)
        res.MC_put_to_storage(rax)
        return res

    def __xor__(self, other):
        res = I64(self.object_manager, value=None)
        I64.int2reg(other, rcx)
        self.MC_get_from_storage(rax)
        xor_(rax, rcx)
        res.MC_put_to_storage(rax)
        return res

    def __rshift__(self, other):
        res = I64(self.object_manager, value=None)
        I64.int2reg(other, rcx)
        self.MC_get_from_storage(rax)
        sar_(rax, cl)
        res.MC_put_to_storage(rax)
        return res

    def __lshift__(self, other):
        res = I64(self.object_manager, value=None)
        I64.int2reg(other, rcx)
        self.MC_get_from_storage(rax)
        sal_(rax, cl)
        res.MC_put_to_storage(rax)
        return res

    def __pos__(self):
        return self

    def __abs__(self):
        res = I64(self.object_manager, value=None)
        self.MC_get_from_storage(rax)
        mov_(rcx, rax)
        neg_(rax)
        cmovl_(rax, rcx)
        res.MC_put_to_storage(rax)
        return res

    def sgn(self):
        res = I64(self.object_manager, value=None)
        self.MC_get_from_storage(rax)
        mov_(rbx, 1)
        mov_(rcx, 1)
        neg_(rcx)
        or_(rax, rax)
        cmovs_(rax, rcx)
        cmovg_(rax, rbx)
        res.MC_put_to_storage(rax)
        return res

    def set_from_const(self, value):
        mov_(rax, value)
        self.MC_put_to_storage(rax)

    def cast_and_store(self, v):
        T = v.type
        if (T.main_type is I32) or (T.main_type is U32):
            xor_(rcx, rcx)
            mov_(rbx, 1)
            neg_(rbx)
            shl_(rbx, 32)
            or_(eax, eax)
            cmovs_(rcx, rbx)
            or_(rax, rcx)
            self.MC_put_to_storage(rax)
            return

        if T.main_type is Float:
            v.MC_get_from_storage(rax)
            fldt_([rax])

            tmp_ptr = self.object_manager.get_current_heap_end_ptr()
            # set Rounded result is closest to but no less than the infinitely precise result.
            movl_([tmp_ptr], 0xf7f)
            fldcw_([tmp_ptr])

            ptr = self.get_ptr()
            fistpq_([ptr])

            movl_([tmp_ptr], 0x37f)
            fldcw_([tmp_ptr])
            return

        if T.main_type in {Byte, U64, I64, Ref, Bool}:
            self.MC_put_to_storage(rax)
        else:
            raise CompilerException(f"no cast from {T} to int")

    def set(self, v):
        v.MC_get_from_storage(rax)
        self.cast_and_store(v)
