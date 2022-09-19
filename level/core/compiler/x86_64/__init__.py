import ast

from level.core.compiler import *
from level.core.compiler import CallAddress

from level.core.compiler.types import Type, TypeVar

from level.core.compiler.x86_64.types.u32 import U32
from level.core.compiler.x86_64.types.i32 import I32
from level.core.compiler.x86_64.types.u64 import U64
from level.core.compiler.x86_64.types.i64 import I64
from level.core.compiler.x86_64.types.float import Float
from level.core.compiler.x86_64.types.bool import Bool
from level.core.compiler.x86_64.types.array import Array
from level.core.compiler.x86_64.types.ref import Ref
from level.core.compiler.x86_64.types.rec import Rec
from level.core.compiler.x86_64.types.byte import Byte

from level.core.parser.builtin import translate_simple_types, BuiltinValue, BuiltinFloat, BuiltinRef

from level.core.x86_64 import *

class StringInfo:
    def __init__(self, s, addr):
        self.s = s
        self.addr = addr

class FloatInfo:
    def __init__(self, s, addr):
        self.s = s
        self.addr = addr

class CompileDriver_x86_64(CompileDriver):
    def __init__(self, compiler):
        self.compiler = compiler
        self.hex_trans = SymBits(bits=64)
        self.new_line = SymBits(bits=64)
        self.u64space = SymBits(bits=64)
        self.exit_addr = SymBits(bits=64)
        self.enter = SymBits(bits=64)
        self.args_addr = SymBits(bits=64)

        self.while_stack = []
        self.if_stack = []

        self.string_table = []
        self.float_table = []

        self.object_type = Type(main_type=Rec, user_name="object")


    def set_args_addr(self):
        mov_(rdi, self.args_addr)
        mov_([rdi], rsp)

    def begin(self):
        begin()
        self.set_args_addr()

    def set_acc(self, i):
        mov_(rax, i)

    def end(self):
        set_symbol(self.exit_addr)
        mov_(rdi, rax)
        mov_(rax, 60)
        syscall_()

    def get_new_address(self):
        addr = SymBits(bits=32)
        # return CallAddress(address())
        return CallAddress(addr)

    def set_call_address(self, addr : CallAddress):
        set_symbol(addr.value)

    def call(self, addr : CallAddress):
        call_(addr.value)

    def ret(self):
        ret_()

    def get_type_by_const(self, c):
        #print(c, c.name)
        if type(c.name) is int:
            return Type(I64)

        if type(c.name) is bool:
            return Type(Bool)

        if type(c.name) is bytes:
            return Type(Ref, sub_types=[Type(Byte)])

        if type(c.name) is ast.U64ConstType:
            return Type(U64)

        if type(c.name) is ast.FloatConstType:
            return Type(Float)

        if type(c.name) is BuiltinFloat:
            return Type(Float)

        if type(c.name) is BuiltinRef:
            return Type(Ref)

        raise CompilerException (f"unknown const symbol '{c.name}' in {c.meta}")

    def get_array_type_by_const(self, c):
        return Type(main_type=Array, length=c.name, sub_types=[Type(U32)])

    def get_ref_type_for_type(self, T):
        return Type(Ref, sub_types=[T])

    def get_ref_type_for_obj(self, obj=None):
        if obj is None:
            return Type(Ref, sub_types=[Type(Byte)])
        else:
            return Type(Ref, sub_types=[obj.type])

    def get_type_by_var(self, c):
        return Type(U32)

    def get_simple_type_by_name(self, t):
        if t.name in translate_simple_types:
            if t.name == 'object':
                return self.object_type
            else:
                return Type(eval(translate_simple_types[t.name]))

        return None

    def get_array_type(self):
        return Array

    def get_ref_type(self):
        return Ref

    def get_rec_type(self):
        return Rec

    def get_empty_type(self):
        return Type(main_type=Rec, length=0)

    def get_bool(self, b, obj_manager):
        res = obj_manager.reserve_variable(Type(Bool), value=b)
        return res

    def bind(self, ref, obj):
        ref.bind(obj)

    def build_ref(self, obj_manager, obj):
        T = self.get_ref_type_for_obj(obj)
        ref = obj_manager.reserve_variable(T)
        self.bind(ref, obj)
        return ref

    def deref(self, ref):
        return ref.get_obj()

    def get_typeid(self, obj_manager, obj):
        if type(obj) is Type:
            res = obj_manager.reserve_variable(Type(U64), hash(obj))
        else:
            res = obj_manager.reserve_variable(Type(U64), hash(obj.type))
        return res

    def get_sizeof(self, obj_manager, obj):
        if type(obj) is Type:
            res = obj_manager.reserve_variable(Type(I64), obj.size())
        else:
            res = obj_manager.reserve_variable(Type(I64), obj.type.size())
        return res

    def unary_operator(self, op_T, obj, obj_manager):
        if op_T is ast.Plus:
            return +obj

        if op_T is ast.Minus:
            return -obj

        if op_T is ast.Not:
            return obj.not_()

        if op_T is ast.BNot:
            return ~obj

        if op_T is ast.Abs:
            return abs(obj)

        if op_T is ast.Sgn:
            return obj.sgn()

        if op_T is ast.Sin:
            return obj.sin()

        if op_T is ast.Cos:
            return obj.cos()

        if op_T is ast.Tan:
            return obj.tan()

        if op_T is ast.Cot:
            return obj.cot()

        if op_T is ast.Sqrt:
            return obj.sqrt()

        if op_T is ast.Floor:
            return obj.floor()

        if op_T is ast.Ceil:
            return obj.ceil()

        if op_T is ast.Log2:
            return obj.log2()

        if op_T is ast.TypeId:
            return self.get_typeid(obj_manager, obj)

        if op_T is ast.SizeOf:
            return self.get_sizeof(obj_manager, obj)

        raise CompilerNotLocatedException("unexpected operator")

    def unify(self, obj1, obj2):
        # print(obj1, obj2)
        # print(obj1.priority, obj2.priority)
        if obj1.type == obj2.type:
            return obj1, obj2

        if obj2.priority > obj1.priority:
            return obj2.type(obj1), obj2
        else:
            return obj1, obj1.type(obj2)

    def operator(self, op_T, obj1, obj2):
        #print(op_T)
        obj1, obj2 = self.unify(obj1, obj2)
        res = None

        if op_T is ast.Add:
            res = obj1 + obj2

        if op_T is ast.AddNoOverride:
            res = obj1 + obj2

        if op_T is ast.Eq:
            res = obj1 == obj2

        if op_T is ast.Neq:
            res = (obj1 != obj2)

        if op_T is ast.Sub:
            res = obj1 - obj2

        if op_T is ast.Lt:
            res = obj1 < obj2

        if op_T is ast.Ge:
            res = obj1 >= obj2

        if op_T is ast.Le:
            res = obj1 <= obj2

        if op_T is ast.Gt:
            res = obj1 > obj2

        if op_T is ast.Mul:
            res = obj1 * obj2

        if op_T is ast.Mod:
            res = obj1 % obj2

        if op_T is ast.Div:
            res = obj1 // obj2

        if op_T is ast.And:
            res = obj1.and_(obj2)

        if op_T is ast.Or:
            res = obj1.or_(obj2)

        if op_T is ast.BAnd:
            res = obj1 & obj2

        if op_T is ast.BOr:
            res = obj1 | obj2

        if op_T is ast.BXor:
            res = obj1 ^ obj2

        if op_T is ast.RShift:
            res = obj1 >> obj2

        if op_T is ast.LShift:
            res = obj1 << obj2

        if res is None:
            raise CompilerNotLocatedException("unexpected operator")
        else:
            return res

    def logic_operator_compile_begin(self, op_T, obj):
        if op_T in {ast.And, ast.Or}:
            jump_address = SymBits()
            obj.to_acc()
            if obj.type != Bool:
                or_(rax, rax)
            if op_T is ast.And:
                jz_(jump_address)
            if op_T is ast.Or:
                jnz_(jump_address)

            return jump_address
        else:
            return None

    def logic_operator_compile_end(self, jump_address, res):
        if jump_address is not None:
            set_symbol(jump_address)
            res.set_by_acc()

    def allocate_brk(self, reg):
        mov_(rdi, 0)
        mov_(rax, 12)
        syscall_()
        add_(rax, reg)
        mov_(rdi, rax)
        mov_(rax, 12)
        syscall_()
        sub_(rax, reg)

    def allocate(self, size):
        # __api__(syscall, 9, 0, 4096, 7, 32 + 2, -1, 0);
        self.syscall(9, 0, (size//4096 + 1)*4096, 7, 34, -1, 0)
        mov_(rbp, rax)


    def set_frame(self, memory):
        self.allocate(memory)
        #mov_(rdi, self.static_brk)
        #mov_([rdi], rax)

    def frame_up(self, shift):
        add_(rbp, shift)

    def frame_down(self, shift):
        sub_(rbp, shift)

    def add_compiler_data(self):
        set_symbol(self.hex_trans)
        add_bytes(b"0123456789abcdef-+:")
        set_symbol(self.u64space)
        add_bytes(bytes(255))
        set_symbol(self.enter)
        add_bytes(b"\n")

        for str_info in self.string_table:
            set_symbol(str_info.addr)
            add_bytes(str_info.s)
            add_bytes(b"\x00")

        for float_info in self.float_table:
            set_symbol(float_info.addr)
            add_bytes(float_info.s)

        set_symbol(self.args_addr)
        add_bytes(bytes(8))


    def echo_obj(self, obj):
        if obj.type.main_type is Ref:
            self.echo_sz(obj)
            self.echo_n()
            return

        obj.to_acc()

        if obj.type.main_type is Float:
            mov_(al, [rax + 9])
            self.echo_acc_handle(bits=8)
            obj.to_acc()
            mov_(al, [rax + 8])
            self.echo_acc_handle(bits=8)
            self.print(self.hex_trans + 18, 1)
            obj.to_acc()
            mov_(rax, [rax])
            self.echo_acc_handle(bits=64)
            self.echo_n()
            return

        if obj.type.main_type is U64:
            self.echo_acc_handle(bits=64)
            self.echo_n()
            return

        if obj.type.main_type is I64:
            self.echo_acc_handle(bits=64, signed=True)
            self.echo_n()
            return

        if obj.type.main_type is I32:
            self.echo_acc_handle(bits=32, signed=True)
            self.echo_n()
            return

        if obj.type.main_type is Byte:
            self.echo_acc_handle(bits=8)
            self.echo_n()
            return

        self.echo_acc_handle(bits=32)
        self.echo_n()

    def print(self, addr, size):
        mov_(rsi, addr)
        mov_(rdx, size)
        mov_(rdi, 1)
        mov_(rax, 1)
        syscall_()

    def echo_acc_handle(self, bits=32, signed=False, break_point=7):
        mov_(rbx, 0)
        mov_(rdi, self.u64space)
        mov_(rsi, self.hex_trans)

        if signed:
            if bits == 64:
                movb_(bl, ord('+'))
                or_(rax, rax)
                cmovl_(ebx, [rsi + 16])
                mov_([rdi], bl)
                inc_(rdi)
                mov_(rcx, rax)
                neg_(rax)
                cmovl_(rax, rcx)
                xor_(rbx, rbx)

            if bits == 32:
                movb_(bl, ord('+'))
                or_(eax, eax)
                cmovl_(ebx, [rsi + 16])
                mov_([rdi], bl)
                inc_(rdi)
                mov_(ecx, eax)
                neg_(eax)
                cmovl_(eax, ecx)
                xor_(rbx, rbx)

        n = bits//4
        if bits == 64:
            shift = 1
        else:
            shift = 0

        for i in range(n):
            mov_(bl, al)
            and_(bl, 0xf)
            mov_(bl, [rsi + rbx])
            mov_([rdi + ((n - 1) - i + shift)], bl)
            shr_(rax, 4)
            if bits == 64 and i == break_point:
                shift = 0
                movb_([rdi + ((n - 1) - i + shift)], ord(':'))

        if bits == 64:
            size = n + 1
        else:
            size = n

        if signed:
            size += 1

        self.print(self.u64space, size)

    def echo_n(self):
        self.print(self.enter, 1)

    def echo_sz(self, obj):
        obj.to_acc()
        xor_(edx, edx)
        loop = address()
        mov_(bl, [rax + edx])
        inc_(edx)
        or_(bl, bl)
        jnz_(loop)
        dec_(edx)
        self.print(eax, edx)
        #self.print(self.enter, 1)

    def ifelse_acc(self, obj_manager, else_= False):
        self.if_stack.append(None)
        end_if_block = SymBits()
        if else_:
            end_else_block = SymBits()
        or_(rax, rax)
        jz_(end_if_block)
        self.compiler.code_block_contexts.open_new(obj_manager, scope_name="ifelse")
        yield None
        self.compiler.code_block_contexts.compile_current_closure()
        self.compiler.code_block_contexts.close_current()

        if else_:
            jmp_(end_else_block)

        set_symbol(end_if_block)

        if else_:
            self.compiler.code_block_contexts.open_new(obj_manager, scope_name="ifelse")
            yield None
            self.compiler.code_block_contexts.compile_current_closure()
            self.compiler.code_block_contexts.close_current()
            set_symbol(end_else_block)

        self.if_stack.pop()
        yield None

    def while_acc(self, obj_manager):
        end_while_block = SymBits()
        continue_addr = SymBits()
        begin_while_block = address()
        yield None
        or_(rax, rax)
        jz_(end_while_block)
        self.while_stack.append((continue_addr, end_while_block))
        self.compiler.code_block_contexts.open_new(obj_manager, scope_name="while")
        yield None
        self.compiler.code_block_contexts.compile_current_closure()
        set_symbol(continue_addr)
        yield None
        jmp_(begin_while_block)
        set_symbol(end_while_block)
        self.compiler.code_block_contexts.close_current()
        self.while_stack.pop()
        # self.compiler.code
        yield None


    def compile_break(self):
        if self.while_stack:
            self.compiler.code_block_contexts.compile_on_break()
            jmp_(self.while_stack[-1][1])

    def compile_continue(self):
        if self.while_stack:
            self.compiler.code_block_contexts.compile_on_continue()
            jmp_(self.while_stack[-1][0])

    def exit(self):
        jmp_(self.exit_addr)

    def syscall(self, *args):
        # all registers except rcx and r11 and rax (return value) are preserved
        if len(args) > 0:
            mov_(rax, args[0])
        if len(args) > 1:
            mov_(rdi, args[1])
        if len(args) > 2:
            mov_(rsi, args[2])
        if len(args) > 3:
            mov_(rdx, args[3])
        if len(args) > 4:
            mov_(r10, args[4])
        if len(args) > 5:
            mov_(r8, args[5])
        if len(args) > 6:
            mov_(r9, args[6])

        syscall_()

    def compile_api_syscall(self, obj_manager, *refs):
        if len(refs) > 0:
            refs[0].MC_get_from_storage(rax)
        if len(refs) > 1:
            refs[1].MC_get_from_storage(rdi)
        if len(refs) > 2:
            refs[2].MC_get_from_storage(rsi)
        if len(refs) > 3:
            refs[3].MC_get_from_storage(rdx)
        if len(refs) > 4:
            refs[4].MC_get_from_storage(r10)
        if len(refs) > 5:
            refs[5].MC_get_from_storage(r8)
        if len(refs) > 6:
            refs[6].MC_get_from_storage(r9)
        syscall_()
        res = obj_manager.reserve_variable(Type(Ref))
        res.MC_put_to_storage(rax)

        return res

    def compile_api_sbrk(self, obj_manager, size_obj):
        res = obj_manager.reserve_variable(Type(Ref))
        size_obj.MC_get_from_storage(rbx)
        self.allocate_brk(rbx)
        res.MC_put_to_storage(rax)
        return res

    def compile_api_args(self, obj_manager):
        res = obj_manager.reserve_variable(Type(Ref, sub_types=[Type(Ref)]))
        mov_(rsi, self.args_addr)
        mov_(rsi, [rsi])
        res.MC_put_to_storage(rsi)
        return res


class StandardObjManager(ObjManager):
    def __init__(self, compiler, subroutine=None, memory=0x100000):
        self.size = SymBits()
        self.cursor = 0
        self.on_top_cursor = 0
        self.parent = None
        self.memory = memory
        ObjManager.__init__(self, compiler, subroutine=subroutine)

    def set_main_frame(self):
        self.compiler.compile_driver.set_frame(self.memory)

    def get_current_heap_end_ptr(self):
        return ebp + self.cursor

    def create_child_obj_manager(self, subroutine):
        self.on_top_cursor = 0
        object_manager = StandardObjManager(self.compiler, subroutine=subroutine)
        object_manager.parent = self
        self.compiler.compile_driver.frame_up(self.size)
        return object_manager

    def close(self):
        if self.parent is None:
            set_symbol(self.size, self.cursor)
        else:
            self.parent.on_top_cursor = 0
            self.compiler.compile_driver.frame_down(self.parent.size)

        ObjManager.close(self)

    def reserve_variable_ptr(self, size, for_child_manager=False):
        if for_child_manager:
            res = rbp + (self.on_top_cursor + self.size)
            self.on_top_cursor = self.on_top_cursor + size
        else:
            res = rbp + self.cursor
            self.cursor = self.cursor + size
        return res

    def reserve_variable(self, T, value=None, for_child_manager=False, copy=False, source_obj=None):
        index = self.cursor
        res = T.main_type(self, T=T, value=value, for_child_manager=for_child_manager, copy=copy)
        res.index = index

        if source_obj is not None:
            res.set(source_obj)

        return res

    def reserve_variable_for_child_obj_manager(self, T, obj=None, value=None):
        res = self.reserve_variable(T, value=value, for_child_manager=True, source_obj=obj)
        return res