from level.core.compiler.types import Obj, Type
import level.core.compiler.x86_64.types.i64
from level.core.compiler.x86_64.types.bool import Bool
from level.core.x86_64 import *
from level.core.compiler import CompilerException

class Float(Obj):
    size = 10
    priority = 32

    def __init__(self,
                 object_manager,
                 value=None,
                 ptr=None,
                 for_child_manager=False,
                 T=None,
                 referenced=False):

        if T is None:
            self.type = Type(Float)
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
            mov_(reg, [self.ptr])
        else:
            lea_(reg, [self.ptr])

    def MC_put_to_storage(self, reg):
        if self.referenced:
            mov_([self.ptr], reg)
        else:
            obj = self.type.main_type(object_manager=None, T=self.type, ptr=reg)
            self.set(obj)

    def get_ptr(self):
        if self.referenced:
            mov_(r15, [self.ptr])
            return r15
        else:
            return self.ptr

    def set_by_acc(self):
        obj = self.type.main_type(object_manager=None, T=self.type, ptr=rax)
        self.set(obj)

    def to_acc(self):
        self.MC_get_from_storage(rax)

    def __neg__(self):
        res = Float(self.object_manager)
        fldt_([self.get_ptr()])
        fchs_()
        fstpt_([res.get_ptr()])
        return res

    def __abs__(self):
        res = Float(self.object_manager)
        fldt_([self.get_ptr()])
        fabs_()
        fstpt_([res.get_ptr()])
        return res

    def __add__(self, other):
        res = Float(self.object_manager)
        fldt_([self.get_ptr()])
        fldt_([other.get_ptr()])
        faddp_()
        fstpt_([res.get_ptr()])
        return res

    def __sub__(self, other):
        res = Float(self.object_manager)
        fldt_([self.get_ptr()])
        fldt_([other.get_ptr()])
        fsubp_()
        fstpt_([res.get_ptr()])
        return res

    def __mul__(self, other):
        res = Float(self.object_manager)
        fldt_([self.get_ptr()])
        fldt_([other.get_ptr()])
        fmulp_()
        fstpt_([res.get_ptr()])
        return res

    def __floordiv__(self, other):
        res = Float(self.object_manager)
        fldt_([self.get_ptr()])
        fldt_([other.get_ptr()])
        fdivp_()
        fstpt_([res.get_ptr()])
        return res

    def __eq__(self, other):
        res = Bool(self.object_manager, value=None)
        fldt_([other.get_ptr()])
        fldt_([self.get_ptr()])
        fcomip_(st(1))
        setz_(al)
        fstp_(st(0))
        res.MC_put_to_storage(al)
        return res

    def __ne__(self, other):
        res = Bool(self.object_manager, value=None)
        fldt_([other.get_ptr()])
        fldt_([self.get_ptr()])
        fcomip_(st(1))
        setnz_(al)
        fstp_(st(0))
        res.MC_put_to_storage(al)
        return res

    def __lt__(self, other):
        res = Bool(self.object_manager, value=None)
        fldt_([other.get_ptr()])
        fldt_([self.get_ptr()])
        fcomip_(st(1))
        setb_(al)
        fstp_(st(0))
        res.MC_put_to_storage(al)
        return res

    def __gt__(self, other):
        res = Bool(self.object_manager, value=None)
        fldt_([other.get_ptr()])
        fldt_([self.get_ptr()])
        fcomip_(st(1))
        seta_(al)
        fstp_(st(0))
        res.MC_put_to_storage(al)
        return res

    def __le__(self, other):
        res = Bool(self.object_manager, value=None)
        fldt_([other.get_ptr()])
        fldt_([self.get_ptr()])
        fcomip_(st(1))
        setbe_(al)
        fstp_(st(0))
        res.MC_put_to_storage(al)
        return res

    def __ge__(self, other):
        res = Bool(self.object_manager, value=None)
        fldt_([other.get_ptr()])
        fldt_([self.get_ptr()])
        fcomip_(st(1))
        setae_(al)
        fstp_(st(0))
        res.MC_put_to_storage(al)
        return res

    def prepare_cast(self, T, v):
        if T.main_type is Float:
            v.MC_get_from_storage(rsi)
            mov_(rax, [rsi])
            mov_([rdi], rax)
            mov_(eax, [rsi + 6])
            mov_([rdi + 6], eax)
            return

        if T.main_type is level.core.compiler.x86_64.types.i64.I64:
            v.MC_get_from_storage(rax)
            mov_([rdi], rax)
            fildq_([rdi])
            fstpt_([rdi])
            return

        raise CompilerException(f"no cast from {T} to Float")

    def set(self, v):
        self.MC_get_from_storage(rdi)
        self.prepare_cast(v.type, v)

    def cast(self, T):
        res = self.object_manager.reserve_variable(T)
        res.set(self)
        return res

    def set_from_const(self, value):
        addr = SymBits(bits=64)
        mov_(rax, addr)
        self.MC_put_to_storage(rax)
        if self.object_manager is not None:
            self.object_manager.compile_driver.float_table.append(level.core.compiler.x86_64.FloatInfo(bytes(value), addr))
        return
