from level.core.x86_64 import *


class _indent:
    def __init__(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, t, value, traceback):
        pass


I = _indent()


class Var:
    @property
    def val(self):
        return None

    @val.setter
    def val(self, value):
        self.set(value)


class PROGRAM:
    def __init__(self):
        begin()
        self.variables = []
        self.hex_trans = self.DATA(b"0123456789abcdef")
        self.n = self.DATA(b"\n")

    def DATA(self, value):
        res = DATA(self, value)
        self.variables.append(res)
        return res

    def U32(self, value=0, context=None):
        res = U32(program=self, value=value, context=context)
        self.variables.append(res)
        return res

    def exit(self):
        mov_(eax, 1)
        mov_(ebx, 0)
        int_(0x80)

        for var in self.variables:
            var.alloc()


class CONTEXT:
    def __init__(self, program):
        self.program = program
        self.virtual_cursor = 0
        self.size = SymBits()

    def __enter__(self):
        subl_(rsp, self.size)
        mov_(rbp, rsp)
        return self

    def __exit__(self, t, value, traceback):
        set_symbol(self.size, self.virtual_cursor)
        addl_(rsp, self.size)
        mov_(rbp, rsp)

    def U32(self, value=0):
        rel_ptr = self.virtual_cursor
        res = self.program.U32(context=self, value=value)
        res.rel_ptr = rel_ptr
        mov_(eax, value)
        res.MC_put_to_storage(eax)
        self.virtual_cursor += 4
        return res


class While:
    def __init__(self, c):
        self.c = c

    def __enter__(self):
        self.end = SymBits()
        self.begin = address()
        self.c.MC_get_from_storage(eax)
        or_(eax, eax)
        jz_(self.end)
        return self

    def __exit__(self, t, value, traceback):
        jmp_(self.begin)
        set_symbol(self.end)


class If:
    class _Then:
        def __init__(self, _if):
            self._if = _if

        def __enter__(self):
            mov_(eax, [self._if.c.ptr])
            or_(eax, eax)
            jz_(self._if.else_)

        def __exit__(self, t, value, traceback):
            jmp_(self._if.end)
            set_symbol(self._if.else_)
            set_symbol(self._if.end)

    class _Else:
        def __init__(self, _if):
            self._if = _if

        def __enter__(self):
            return self

        def __exit__(self, t, value, traceback):
            set_symbol(self._if.end)

    def __init__(self, c):
        self.c = c
        self.end = SymBits()
        self.else_ = SymBits()

    def Then(self):
        return If._Then(self)

    def Else(self):
        return If._Else(self)

    def __enter__(self):
        return self

    def __exit__(self, t, value, traceback):
        pass


class DATA:
    def __init__(self, program, value):
        self.program = program
        self.value = value
        self.size = len(value)
        self.ptr = SymBits()

    def alloc(self):
        set_symbol(self.ptr)
        add_bytes(self.value)

    def print(self):
        mov_(edx, self.size)
        mov_(ecx, self.ptr)
        mov_(ebx, 1)
        mov_(eax, 4)
        int_(0x80)
        mov_(eax, 1)

    def println(self):
        self.print()
        self.program.n.print()

    def set(self, v):
        mov_(eax, self.size)
        loop = address()
        dec_(eax)
        mov_(bl, [eax + v.ptr])
        mov_([eax + self.ptr], bl)
        or_(eax, eax)
        jnz_(loop)


class U32(Var):
    def __init__(self, program, value=0, context=None):
        self.program = program
        self.context = context
        self.value = value
        self.ptr = SymBits()
        self.rel_ptr = 0
        self.provider = program
        self.size = 4

    def alloc(self):
        set_symbol(self.ptr)
        add_bytes(u32(self.value))

    def MC_get_from_storage(self, reg):
        if self.context is None:
            mov_(reg, [self.ptr])
        else:
            mov_(reg, [rbp + self.rel_ptr])

    def MC_put_to_storage(self, reg):
        if self.context is None:
            mov_([self.ptr], reg)
        else:
            mov_([rbp + self.rel_ptr], reg)

    def __add__(self, other):
        res = self.provider.U32()
        if type(other) is int:
            mov_(edx, other)
        else:
            other.MC_get_from_storage(edx)

        self.MC_get_from_storage(eax)
        add_(eax, edx)
        res.MC_put_to_storage(eax)
        return res

    def __radd__(self, other):
        return self.__add__(other)

    def repr(self):
        self.MC_get_from_storage(eax)
        data = self.program.DATA(bytes(8))
        mov_(rbx, 0)
        for i in range(8):
            mov_(bl, al)
            and_(bl, 0xf)
            mov_(bl, [ebx + self.program.hex_trans.ptr])
            mov_([data.ptr + (7 - i)], bl)
            ror_(eax, 4)

        return data

    def __eq__(self, other):
        res = self.provider.U32()

        if type(other) is int:
            mov_(ecx, other)
        else:
            other.MC_get_from_storage(ecx)

        self.MC_get_from_storage(eax)
        xor_(eax, ecx)
        setz_(al)
        and_(eax, 0xff)
        res.MC_put_to_storage(eax)
        return res

    def __ne__(self, other):
        res = self.provider.U32()
        if type(other) is int:
            mov_(ecx, other)
        else:
            other.MC_get_from_storage(ecx)

        self.MC_get_from_storage(eax)
        xor_(eax, ecx)
        setnz_(al)
        and_(eax, 0xff)
        res.MC_put_to_storage(eax)
        return res

    def set(self, v):
        v.MC_get_from_storage(eax)
        self.MC_put_to_storage(eax)