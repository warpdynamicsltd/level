import random
import string
import inspect
from inspect import signature
from level.core.x86_64 import *
from importlib import reload, import_module

class LevelException(Exception):
    pass

class _indent:
    def __init__(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, t, value, traceback):
        pass


I = _indent()

def stack_variables(*args):
    cursor = CONTEXT.current_context.size

    for a in args:
        u = U32(ptr=cursor)
        u.set(a)
        cursor = cursor + u.size

def unstack_variables(context, n):
    args = []

    for i in range(n):
        u = U32(ptr=context.virtual_cursor)
        args.append(u)
        context.virtual_cursor = context.virtual_cursor + u.size

    return args

def function_call_no_return(start, *args):
    stack_variables(*args)

    with CONTEXT(CONTEXT.current_context) as c:
        call_(start)

def function_call_return(start, *args):
    stack_variables(*args)

    with CONTEXT(CONTEXT.current_context) as c:
        call_(start)

    z = U32()
    z.MC_put_to_storage(eax)
    return z

def function(f):
    # In order to make recursion work, we first take a code of function f
    # and define a function with changed name which has the same definition body as f
    # this is for a case, when f is calling itself

    random_prefix = ''.join(random.choices(string.ascii_lowercase, k=50))
    code = inspect.getsource(f)
    code = f'global {f.__name__}, {random_prefix}_{f.__name__}\ndef {random_prefix}_' + code[14:]

    global current_context
    if PROGRAM.program is None:
        raise LevelException("PROGRAM() hasn't been called")

    s = signature(f)
    n = len(s.parameters)
    end = SymBits()
    jmp_(end)
    start = address()

    # now, we redefine function f to be call to code of function f (which execution of renamed function f will produce)
    # but where renamed function will be calling f this code will be injected

    # usage of globals in exec is necessary
    # because it can't assign properly local variables as functions due to Python optimisations
    mc_return = f"""
global {f.__name__}, {random_prefix}_{f.__name__}
def {f.__name__}(*args_):
    return function_call_return({start}, *args_)
"""

    mc_none = f"""
global {f.__name__}, {random_prefix}_{f.__name__}
def {f.__name__}(*args_):
    return function_call_no_return({start}, *args_)
"""

    # we need to establish if f returns value or not
    # Level functions are required to have only one return at the end of the function definition

    mc = mc_none
    for line in code.split('\n'):
        line = line.strip()
        if line[:6] == 'return':
            mc = mc_return

    exec(mc_return)
    exec(code)


    with FUNCTION_DEFINITION(CONTEXT.current_context) as c:
        args = unstack_variables(c, n)
        # for i in range(n):
        #     u = U32(ptr=c.virtual_cursor)
        #     args.append(u)
        #     c.virtual_cursor = c.virtual_cursor + u.size

        # finally we execute renamed function f, which will build its code

        y = eval(f"{random_prefix}_{f.__name__}(*args)")

        if y is not None:
            y.MC_get_from_storage(eax)

    ret_()
    set_symbol(end)

    def result(*args_):
        if y is not None:
            return function_call_return(start, *args_)
        else:
            return function_call_no_return(start, *args_)

    # function which will call to the function f machine code is returned
    return result


class Var:
    @property
    def val(self):
        return None

    @val.setter
    def val(self, value):
        self.set(value)


def INCLUDE(x):
    mymodule = import_module(x)
    reload(mymodule)


class CONTEXT:
    current_context = None
    def __init__(self, parent=current_context):

        self.parent = parent
        self.virtual_cursor = 0
        self.size = SymBits()
        if parent is not None:
            self.offset = self.parent.offset + self.parent.size
            self.program = self.parent.program
        else:
            self.offset = SymBits()

    def __enter__(self):
        CONTEXT.current_context = self
        if self.parent is not None:
            add_(ebp, self.parent.size)
        return self

    def __exit__(self, t, value, traceback):
        set_symbol(self.size, self.virtual_cursor)
        sub_(ebp, self.parent.size)
        CONTEXT.current_context = self.parent

    def U32(self, res, value=0):
        #res = U32(context=self, value=value)
        res.program = self.program
        res.ptr = self.virtual_cursor
        if value is not None:
            movl_([ebp + res.ptr], value)
        self.virtual_cursor = self.virtual_cursor + 4
        return res

class FUNCTION_DEFINITION(CONTEXT):
    def __init__(self, parent=CONTEXT.current_context):
        CONTEXT.__init__(self, parent)
        self.program = PROGRAM.program
        self.offset = 0

    def __exit__(self, t, value, traceback):
        set_symbol(self.size, self.virtual_cursor)
        CONTEXT.current_context = None


class PROGRAM(CONTEXT):
    def __init__(self, parent=None):
        PROGRAM.program = self
        CONTEXT.__init__(self, parent)
        self.program = self
        self.variables = []
        CONTEXT.current_context = None
        begin()
        self.hex_trans = self.DATA(b"0123456789abcdef")
        self.n = self.DATA(b"\n")

    def __enter__(self):
        CONTEXT.current_context = self
        mov_(ebp, self.offset)
        return self

    def DATA(self, value):
        res = DATA(self, value)
        self.variables.append(res)
        return res

    def __exit__(self, t, value, traceback):
        mov_(eax, 1)
        mov_(ebx, 0)
        int_(0x80)

        for v in self.variables:
            v.alloc()

        set_symbol(self.offset)
        set_symbol(self.size, self.virtual_cursor)


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
            self._if.c.MC_get_from_storage(eax)
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
    @classmethod
    def int2reg(cls, i, reg):
        if type(i) is int:
            mov_(reg, i)
        else:
            i.MC_get_from_storage(reg)

    def __init__(self, value=0, ptr=None, volatile=False):
        self.size = 4
        self.volatile = volatile
        if CONTEXT.current_context is None:
            raise LevelException("with PROGRAM() required")
        self.program = None
        self.value = value
        self.ptr = SymBits()
        if ptr is None:
            CONTEXT.current_context.U32(self, value)
        else:
            self.ptr = ptr
            self.program = PROGRAM.program

    # def alloc(self):
    #     set_symbol(self.ptr)
    #     add_bytes(u32(self.value))

    def MC_get_from_storage(self, reg):
        mov_(reg, [ebp + self.ptr])

    def MC_put_to_storage(self, reg):
        mov_([ebp + self.ptr], reg)

    def __add__(self, other):
        res = U32(value=None)

        # if type(other) is int:
        #     movl_([ebp + res.ptr], other)
        #     mov_(eax, [ebp + self.ptr])
        #     add_([ebp + res.ptr], eax)
        #     return res
        #
        # else:
        # #if type(other) is U32:
        #     mov_(eax, [ebp + self.ptr])
        #     mov_(ecx, [ebp + other.ptr])
        #     add_(eax, ecx)
        #     mov_([ebp + res.ptr], eax)
        #
        #     return res
        U32.int2reg(other, ecx)

        self.MC_get_from_storage(eax)
        add_(eax, ecx)
        res.MC_put_to_storage(eax)
        return res

    def __sub__(self, other):
        res = U32(value=None)
        U32.int2reg(other, ecx)
        self.MC_get_from_storage(eax)
        sub_(eax, ecx)
        res.MC_put_to_storage(eax)
        return res

    def __mul__(self, other):
        res = U32(value=None)
        if type(other) is int:
            movl_([ebp + res.ptr], other)
            mov_(eax, [ebp + self.ptr])
            mul_([ebp + res.ptr])
            return res

        else:
        #if type(other) is U32:
            mov_(eax, [ebp + self.ptr])
            mov_(ecx, [ebp + other.ptr])
            mul_(ecx)
            mov_([ebp + res.ptr], eax)

            return res
        # res = U32(value=None)
        # U32.int2reg(other, ecx)
        #
        # self.MC_get_from_storage(eax)
        # mul_(ecx)
        # res.MC_put_to_storage(eax)
        # return res

    def  __rsub__(self, other):
        res = U32(value=None)
        U32.int2reg(other, ecx)
        self.MC_get_from_storage(eax)
        sub_(ecx, eax)
        res.MC_put_to_storage(eax)
        return res

    def __radd__(self, other):
        return self.__add__(other)

    def __rmul__(self, other):
        return self.__rmul__(other)

    def add(self, other):
        if type(other) is int:
            addl_([ebp + self.ptr], other)

        if type(other) is U32:
            other.MC_get_from_storage(eax)
            add_([ebp + self.ptr], eax)

    def mul(self, other):
        if type(other) is int:
            mov_(eax, other)
            mul_([ebp + self.ptr])

        if type(other) is U32:
            other.MC_get_from_storage(eax)
            mul_([ebp + self.ptr])

    def __iadd__(self, other):
        self.add(other)
        return self

    def __truediv__(self, other):
        res = U32(value=None)
        self.MC_get_from_storage(eax)
        U32.int2reg(other, ecx)
        xor_(edx, edx)
        div_(ecx)
        res.MC_put_to_storage(eax)
        return res

    def __mod__(self, other):
        res = U32(value=None)
        self.MC_get_from_storage(eax)
        U32.int2reg(other, ecx)
        xor_(edx, edx)
        div_(ecx)
        res.MC_put_to_storage(edx)
        return res

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
        res = U32(value=None)

        if type(other) is int:
            mov_(eax, other)
            xor_(eax, [ebp + self.ptr])
        else:
            mov_(eax, [ebp + other.ptr])
            xor_(eax, [ebp + self.ptr])

        setz_(al)
        and_(eax, 0xff)
        res.MC_put_to_storage(eax)
        return res

    def __ne__(self, other):
        res = U32(value=None)

        if type(other) is int:
            mov_(eax, other)
            xor_(eax, [ebp + self.ptr])
        else:
            mov_(eax, [ebp + other.ptr])
            xor_(eax, [ebp + self.ptr])

        setnz_(al)
        and_(eax, 0xff)
        res.MC_put_to_storage(eax)
        return res

    def __lt__(self, other):
        res = U32(value=None)
        xor_(eax, eax)
        if type(other) is int:
            mov_(ecx, [ebp + self.ptr])
            sub_(ecx, other)
        else:
            mov_(ecx, [ebp + self.ptr])
            sub_(ecx, [ebp + other.ptr])

        setc_(al)
        res.MC_put_to_storage(eax)
        return res

    def __gt__(self, other):
        res = U32(value=None)
        xor_(eax, eax)
        if type(other) is int:
            mov_(ecx, other)
            sub_(ecx, [ebp + self.ptr])
        else:
            mov_(ecx, [ebp + other.ptr])
            sub_(ecx, [ebp + self.ptr])

        setc_(al)
        res.MC_put_to_storage(eax)
        return res

    def __le__(self, other):
        res = U32(value=None)
        xor_(eax, eax)
        if type(other) is int:
            mov_(ecx, other)
            sub_(ecx, [ebp + self.ptr])
        else:
            mov_(ecx, [ebp + other.ptr])
            sub_(ecx, [ebp + self.ptr])

        setnc_(al)
        res.MC_put_to_storage(eax)
        return res

    def __ge__(self, other):
        res = U32(value=None)
        xor_(eax, eax)
        if type(other) is int:
            mov_(ecx, [ebp + self.ptr])
            sub_(ecx, other)
        else:
            mov_(ecx, [ebp + self.ptr])
            sub_(ecx, [ebp + other.ptr])

        setnc_(al)
        res.MC_put_to_storage(eax)
        return res

    def __imatmul__(self, other):
        U32.int2reg(other, eax)
        self.MC_put_to_storage(eax)
        return self

    def set(self, v):
        v.MC_get_from_storage(eax)
        self.MC_put_to_storage(eax)




