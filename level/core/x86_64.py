import struct
from collections import defaultdict

from level.mathtools import *
from level.core.buffer import Buffer

"""
Machine code low level compilation functions
"""


class MachineException(Exception):
    pass


EAX = 0b000
ECX = 0b001
EDX = 0b010
SIB = 0b100
EBX = 0b011
NON = 0b100
ESP = 0b100
EBP = 0b101
NBS = 0b101
DIS = 0b101
ESI = 0b110
EDI = 0b111

R8  = 0b1000
R9  = 0b1001
R10 = 0b1010
R11 = 0b1011
R12 = 0b1100
R13 = 0b1101
R14 = 0b1110
R15 = 0b1111

class Symbol:
    _id = 1
    pass


class SymBits(Symbol):
    def __init__(self, bits=32, signed=True):
        Symbol._id += 1
        self.name = Symbol._id
        self.bits = bits
        self.left = None
        self.right = None
        self.factor = 1
        self.resolved_value = None
        self.signed = signed

    def __repr__(self):
        return str(dict(name=self.name, bits=self.bits, signed=self.signed))

    def pack(self):
        if self.bits == 32:
            if self.signed:
                return i32(self.resolved_value)
            else:
                return u32(self.resolved_value)
        if self.bits == 64:
            if self.signed:
                return i64(self.resolved_value)
            else:
                return u64(self.resolved_value)

    def add(self, factor, other):
        if type(other) is int:
            other_sym = SymBits(self.bits)
            other_sym.resolved_value = other
            res = SymBits(self.bits)
            res.left = (1, self)
            res.right = (factor, other_sym)
            return res

        if type(other) is SymBits:
            res = SymBits()
            res.left = (1, self)
            res.right = (factor, other)
            res.bits = max(self.bits, other.bits)
            return res

        raise MachineException('Unexpected end')

    def __add__(self, other):
        return self.add(1, other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.add(-1, other)

    def __rsub__(self, other):
        return other.__sub__(self)


    def resolve(self):
        if self.resolved_value is not None:
            return

        self.left[1].resolve()
        self.right[1].resolve()

        self.resolved_value = self.left[0]*self.left[1].resolved_value + self.right[0]*self.right[1].resolved_value


class Register:
    def __init__(self, reg, scale=1, dis=0, dis_reg=None, bits=32):
        self.reg = reg
        self.scale = scale
        self.dis_reg = dis_reg
        self.dis = dis
        self.bits = bits

    def __mul__(self, x):
        if x not in {1, 2, 4, 8}:
            raise MachineException("Wrong scaled index")
        if self.scale != 1:
            raise MachineException("Too many multiplications")
        return Register(self.reg, self.scale * x, dis=self.dis)

    def __rmul__(self, x):
        return self * x

    def __add__(self, a):
        if (type(a) is int or issubclass(type(a), Symbol)) and self.dis == 0:
            return Register(self.reg, self.scale, dis=a, dis_reg=self.dis_reg)

        if type(a) is Register and self.dis_reg is None:
            return Register(self.reg, self.scale, dis=self.dis, dis_reg=a)

        raise MachineException("Too many summands")

    def __sub__(self, a):
        if (type(a) is int) and self.dis == 0:
            return Register(self.reg, self.scale, dis=-a, dis_reg=self.dis_reg)

        raise MachineException("Unexpected subtraction")
    def bare(self):
        return self.scale == 1 and self.dis == 0

    def __repr__(self):
        return str(dict(reg=self.reg, bits=self.bits, scale=self.scale, dis=self.dis))


eax = Register(EAX)
ecx = Register(ECX)
edx = Register(EDX)
ebx = Register(EBX)
esp = Register(ESP)
esi = Register(ESI)
edi = Register(EDI)
ebp = Register(EBP)

rax = Register(EAX, bits=64)
rcx = Register(ECX, bits=64)
rdx = Register(EDX, bits=64)
rbx = Register(EBX, bits=64)
rsp = Register(ESP, bits=64)
rsi = Register(ESI, bits=64)
rdi = Register(EDI, bits=64)
rbp = Register(EBP, bits=64)

r8 = Register(R8, bits=64)
r9 = Register(R9, bits=64)
r10 = Register(R10, bits=64)
r11 = Register(R11, bits=64)
r12 = Register(R12, bits=64)
r13 = Register(R13, bits=64)
r14 = Register(R14, bits=64)
r15 = Register(R15, bits=64)

r8d = Register(R8, bits=32)
r9d = Register(R9, bits=32)
r10d = Register(R10, bits=32)
r11d = Register(R11, bits=32)
r12d = Register(R12, bits=32)
r13d = Register(R13, bits=32)
r14d = Register(R14, bits=32)
r15d = Register(R15, bits=32)

al = Register(EAX, bits=8)
cl = Register(ECX, bits=8)
dl = Register(EDX, bits=8)
bl = Register(EBX, bits=8)
ah = Register(ESP, bits=8)
ch = Register(EBP, bits=8)
dh = Register(ESI, bits=8)
bh = Register(EDI, bits=8)

r8b = Register(R8, bits=8)
r9b = Register(R9, bits=8)
r10b = Register(R10, bits=8)
r11b = Register(R11, bits=8)
r12b = Register(R12, bits=8)
r13b = Register(R13, bits=8)
r14b = Register(R14, bits=8)
r15b = Register(R15, bits=8)


def mod_rm_(mod, rm, reg):
    return int((0b111 & mod) << 6 | (0b111 & reg) << 3 | (0b111 & rm))


def sib_(ss, index, base):
    """
    [base + (1^ss)*index]
    """
    return int((0b111 & ss) << 6 | (0b111 & index) << 3 | (0b111 & base))


def rex_(w, r, x, b):
    return 0b01000000 | w << 3 | r << 2 | x << 1 | b


def u8(i):
    return struct.pack('B', i)


def i8(i):
    return struct.pack('b', i)

def u16(i):
    return struct.pack('H', i)

def u32(i):
    if type(i) is int:
        return struct.pack('I', i)
    if issubclass(type(i), Symbol):
        return i


def u64(i):
    if type(i) is int:
        return struct.pack('Q', i)
    if issubclass(type(i), Symbol):
        return i


def i32(i):
    if type(i) is int:
        return struct.pack('i', i)
    if issubclass(type(i), Symbol):
        return i
    #return struct.pack('i', i)

def i64(i):
    if type(i) is int:
        return struct.pack('q', i)
    if issubclass(type(i), Symbol):
        return i


def is_u8(i):
    return type(i) is int and 0 <= i <= 0xff


def is_i8(i):
    return type(i) is int and -0x80 <= i <= 0x7f


def is_u32(i):
    return (type(i) is int and 0 <= i <= 0xffffffff) or (issubclass(type(i), Symbol) and i.bits == 32)


def is_i32(i):
    return (type(i) is int and -0x80000000 <= i <= 0x7fffffff) or ((issubclass(type(i), Symbol) and i.bits == 32 and i.signed))

def is_u64(i):
    return (type(i) is int and 0 <= i <= 0xffffffffffffffff) or (issubclass(type(i), Symbol) and i.bits == 64)

def is_i64(i):
    return (type(i) is int and -0x8000000000000000 <= i <= 0x7fffffffffffffff)


def com(prefixes, opcode, mod_rm, sib, dis, imm):
    if issubclass(type(dis), Symbol):
        bs = bytes(dis.bits//8)
        to_sib = bytes(prefixes) + bytes(opcode) + bytes(mod_rm) + bytes(sib)
        begin.symbols[dis.name].append((begin.buffer.cursor + len(to_sib), dis))
        dis = bs
    else:
        to_sib = bytes(prefixes) + bytes(opcode) + bytes(mod_rm) + bytes(sib)

    if issubclass(type(imm), Symbol):
        bs = bytes(imm.bits//8)
        to_dis = to_sib + bytes(dis)
        begin.symbols[imm.name].append((begin.buffer.cursor + len(to_dis), imm))
        imm = bs
    else:
        to_dis = to_sib + bytes(dis)

    begin.buffer.write(to_dis + bytes(imm))


def op_plus_r_imm(op, reg, imm=[], prefixes=[]):
    #print(reg)
    if reg & 0b1000 == 0b1000:
        #prefixes = [rex_prefix(base=reg, operand_bits=64)]
        prefixes = [rex_(w=1, b=1, r=0, x=0)]
    com(prefixes=prefixes,
        opcode=op[:-1] + [op[-1] + (0b111 & reg)],
        mod_rm=[],
        sib=[],
        dis=[],
        imm=imm)


def op_imm(op, imm=[], prefixes=[]):
    com(prefixes=prefixes,
        opcode=op,
        mod_rm=[],
        sib=[],
        dis=[],
        imm=imm)


def op_modrm(op, mod, rm, reg, ss=None, index=None, base=None, dis=[], imm=[], prefixes=[]):
    if (ss is not None) and (index is not None) and (base is not None):
        com(prefixes=prefixes,
            opcode=op,
            mod_rm=[mod_rm_(mod, rm, reg)],
            sib=[sib_(ss, index, base)],
            dis=dis,
            imm=imm)
        return

    if (ss is None) or (index is None) or (base is None):
        com(prefixes=prefixes,
            opcode=op,
            mod_rm=[mod_rm_(mod, rm, reg)],
            sib=[],
            dis=dis,
            imm=imm)
        return

    raise MachineException('Unexpected end')

def rex_prefix(reg=0, rm=0, index=0, base=0, operand_bits=32):
    r = (0b1000 & reg) >> 3
    if rm != SIB:
        b = (0b1000 & rm) >> 3
        x = 0
    else:
        b = (0b1000 & base) >> 3
        x = (0b1000 & index) >> 3

    w = 1 if operand_bits == 64 else 0
    return rex_(w, r, x, b)

def op_mr_immr(op, d_reg, target, imm=[], prefixes=[], operand_bits=32):
    """
    For instructions of type:
        [0xc6 /0] MOV r/m8, imm8
        [0xc7 /0] MOV r/m32, imm32

        [0x88 /r] MOV r/m8, r8
        [0x89 /r] MOV r/m32, r32
    Parameters
    ----------
    op: list
        list of opcodes for instruction
    d_reg:
        if instruction is in a form [op /d] d_reg is digit;
        if instruction is in a form [op /r] d_reg is register id;
    target: list or Register
        target is list with Register object if operand is in memory (m8 or m32);
        target is Register if operand is in register (r8 or r32)
    imm: bytes or empty list, default=[]
        immediate value if required;
        if not required it is an empty list
    Returns
    -------

    """
    ex = {1: 0, 2: 1, 4: 2, 8: 3}
    if type(target) is list:
        x = target[0]
        if type(x) is Register:
            if x.scale == 1:
                if x.dis == 0 and x.dis_reg is not None:
                    if x.dis_reg.reg == 'ebp':
                        raise MachineException('ebp must be first')
                    if x.bits == 64 or operand_bits == 64:
                        prefixes = [rex_prefix(reg=d_reg, rm=SIB, index=x.reg, base=x.dis_reg.reg, operand_bits=operand_bits)]
                    elif (d_reg | x.reg | x.dis_reg.reg) & 0b1000 == 0b1000:
                        prefixes = [rex_prefix(reg=d_reg, rm=SIB, index=x.reg, base=x.dis_reg.reg, operand_bits=operand_bits)]
                    op_modrm(prefixes=prefixes,
                             op=op,
                             mod=0,
                             rm=SIB,
                             reg=d_reg,
                             ss=ex[x.scale],
                             index=x.reg,
                             base=x.dis_reg.reg,
                             imm=imm)
                    return
            if x.scale in ex:
                if x.dis_reg is None:
                    if x.bits == 64 or operand_bits == 64:
                        prefixes = [rex_prefix(reg=d_reg, rm=SIB, index=x.reg, base=NBS, operand_bits=operand_bits)]
                    elif (d_reg | x.reg ) & 0b1000 == 0b1000:
                        prefixes = [rex_prefix(reg=d_reg, rm=SIB, index=x.reg, base=NBS, operand_bits=operand_bits)]

                    op_modrm(prefixes=prefixes,
                             op=op,
                             mod=0,
                             rm=SIB,
                             reg=d_reg,
                             ss=ex[x.scale],
                             index=x.reg,
                             base=NBS,
                             dis=i32(x.dis),
                             imm=imm)
                else:
                    if x.dis_reg.reg == 'ebp':
                        raise MachineException('ebp must be first')
                    if x.bits == 64 or operand_bits == 64:
                        prefixes = [rex_prefix(reg=d_reg, rm=SIB, index=x.reg, base=x.dis_reg.reg, operand_bits=operand_bits)]
                    elif (d_reg | x.reg | x.dis_reg.reg) & 0b1000 == 0b1000:
                        prefixes = [rex_prefix(reg=d_reg, rm=SIB, index=x.reg, base=x.dis_reg.reg, operand_bits=operand_bits)]
                    op_modrm(prefixes=prefixes,
                             op=op,
                             mod=2,
                             rm=SIB,
                             reg=d_reg,
                             ss=ex[x.scale],
                             index=x.reg,
                             base=x.dis_reg.reg,
                             dis=i32(x.dis),
                             imm=imm)
                return

        if is_u32(x):
            if operand_bits == 64:
                prefixes = [rex_prefix(reg=d_reg, rm=SIB, index=NON, base=NBS, operand_bits=operand_bits)]
            if d_reg & 0b1000 == 0b1000:
                prefixes = [rex_prefix(reg=d_reg, rm=SIB, index=NON, base=NBS, operand_bits=operand_bits)]
            op_modrm(prefixes=prefixes,
                     op=op,
                     mod=0,
                     rm=SIB,
                     reg=d_reg,
                     ss=0,
                     index=NON,
                     base=NBS,
                     dis=i32(x),
                     imm=imm)
            return

    if type(target) is Register:
        if target.bits == 64:
            prefixes = [rex_prefix(reg=d_reg, rm=target.reg, operand_bits=64)]
        elif (d_reg | target.reg) & 0b1000 == 0b1000:
            prefixes = [rex_prefix(reg=d_reg, rm=target.reg, operand_bits=32)]
        op_modrm(prefixes=prefixes,
                 op=op,
                 mod=3,
                 rm=target.reg,
                 reg=d_reg,
                 imm=imm)
        return

    raise MachineException('Unexpected end')


def op_combo(a, b,
             op_rm_r8=[],
             op_rm_r32=[],
             op_r_rm8=[],
             op_r_rm32=[],
             op_r_imm8=[],
             op_r_imm32=[]):

    if (type(a) is list and type(b) is Register) or (type(a) is Register and type(b) is Register):
        if op_rm_r32 and b.bits == 64:
            op_mr_immr(op=op_rm_r32, d_reg=b.reg, target=a, prefixes=[0x48], operand_bits=64)
            return
        if op_rm_r32 and b.bits == 32:
            op_mr_immr(op=op_rm_r32, d_reg=b.reg, target=a)
            return
        if op_rm_r8 and b.bits == 8:
            op_mr_immr(op=op_rm_r8, d_reg=b.reg, target=a)
            return

    if (type(a) is Register and type(b) is Register) or (type(a) is Register and type(b) is list):
        if op_r_rm32 and a.bits == 64:
            op_mr_immr(op=op_r_rm32, d_reg=a.reg, target=b, prefixes=[0x48], operand_bits=64)
            return
        if op_r_rm32 and a.bits == 32:
            op_mr_immr(op=op_r_rm32, d_reg=a.reg, target=b)
            return
        if op_r_rm8 and a.bits == 8:
            op_mr_immr(op=op_r_rm8, d_reg=a.reg, target=b)
            return

    # print(a, b, is_u64(b))

    if op_r_imm32 and type(a) is Register and a.bits == 64 and is_u64(b):
        op_plus_r_imm(op=op_r_imm32, reg=a.reg, imm=u64(b), prefixes=[0x48])
        return

    if op_r_imm32 and type(a) is Register and a.bits == 64 and is_i64(b):
        op_plus_r_imm(op=op_r_imm32, reg=a.reg, imm=i64(b), prefixes=[0x48])
        return

    if op_r_imm32 and type(a) is Register and a.bits == 32 and is_u32(b):
        op_plus_r_imm(op=op_r_imm32, reg=a.reg, imm=u32(b))
        return

    if op_r_imm32 and type(a) is Register and a.bits == 32 and is_i32(b):
        op_plus_r_imm(op=op_r_imm32, reg=a.reg, imm=i32(b))
        return

    if op_r_imm8 and type(a) is Register and a.bits == 8 and is_u8(b):
        op_plus_r_imm(op=op_r_imm8, reg=a.reg, imm=u8(b))
        return

    if op_r_imm8 and type(a) is Register and a.bits == 8 and is_i8(b):
        op_plus_r_imm(op=op_r_imm8, reg=a.reg, imm=i8(b))
        return

    raise MachineException('Unexpected end')


def logic_gate(a, b, op_eax_imm, op_imm_, d, u, prefixes=[]):
    if type(a) is Register and is_u32(b):
        if a.reg == EAX:
            op_imm(op=op_eax_imm, imm=u(b), prefixes=prefixes)
        else:
            op_mr_immr(op=op_imm_, d_reg=d, target=a, imm=u(b), prefixes=prefixes)
        return

    raise MachineException('Unexpected end')


"""
Assembly Mnemonics
"""


def int_(a):
    op_imm(op=[0xcd], imm=u8(a))

def syscall_():
    op_imm(op=[0x0f, 0x05])

def lea_(a, b):
    op_mr_immr(op=[0x8d], d_reg=a.reg, target=b, operand_bits=a.bits)

def mov_(a, b):
    op_combo(op_rm_r8=[0x88],
             op_rm_r32=[0x89],
             op_r_rm8=[0x8a],
             op_r_rm32=[0x8b],
             op_r_imm8=[0xb0],
             op_r_imm32=[0xb8],
             a=a,
             b=b)

# def movq_(a, b):
#     op_mr_immr(op=[0xb8], d_reg=0, target=a, imm=u64(b), operand_bits=64)

def movl_(a, b):
    op_mr_immr(op=[0xc7], d_reg=0, target=a, imm=u32(b))


def movb_(a, b):
    op_mr_immr(op=[0xc6], d_reg=0, target=a, imm=u8(b))


def mul_(a):
    if a.bits == 64:
        op_mr_immr(op=[0xf7], d_reg=4, target=a, prefixes=[0x48])
        return
    if a.bits == 32:
        op_mr_immr(op=[0xf7], d_reg=4, target=a)
        return
    if a.bits == 8:
        op_mr_immr(op=[0xf6], d_reg=4, target=a)
        return

def mulb_(a):
    op_mr_immr(op=[0xf6], d_reg=4, target=a)

def mull_(a):
    op_mr_immr(op=[0xf7], d_reg=4, target=a)

def mulq_(a):
    op_mr_immr(op=[0xf7], d_reg=4, target=a, operand_bits=64)

def imul_(a):
    if a.bits == 64:
        op_mr_immr(op=[0xf7], d_reg=5, target=a, prefixes=[0x48])
        return
    if a.bits == 32:
        op_mr_immr(op=[0xf7], d_reg=5, target=a)
        return
    if a.bits == 8:
        op_mr_immr(op=[0xf6], d_reg=5, target=a)
        return

def imulb_(a):
    op_mr_immr(op=[0xf6], d_reg=5, target=a)


def imull_(a):
    op_mr_immr(op=[0xf7], d_reg=5, target=a)

def div_(a):
    if a.bits == 64:
        op_mr_immr(op=[0xf7], d_reg=6, target=a, prefixes=[0x48])
        return
    if a.bits == 32:
        op_mr_immr(op=[0xf7], d_reg=6, target=a)
        return
    if a.bits == 8:
        op_mr_immr(op=[0xf6], d_reg=6, target=a)
        return

def divb_(a):
    op_mr_immr(op=[0xf6], d_reg=6, target=a)


def divl_(a):
    op_mr_immr(op=[0xf7], d_reg=6, target=a)

def idiv_(a):
    if a.bits == 64:
        op_mr_immr(op=[0xf7], d_reg=7, target=a, prefixes=[0x48])
        return
    if a.bits == 32:
        op_mr_immr(op=[0xf7], d_reg=7, target=a)
        return
    if a.bits == 8:
        op_mr_immr(op=[0xf6], d_reg=7, target=a)
        return

def idivb_(a):
    op_mr_immr(op=[0xf6], d_reg=7, target=a)


def idivl_(a):
    op_mr_immr(op=[0xf7], d_reg=7, target=a)


def not_(a):
    if a.bits == 64:
        op_mr_immr(op=[0xf7], d_reg=2, target=a)
        return
    if a.bits == 32:
        op_mr_immr(op=[0xf7], d_reg=2, target=a)
        return
    if a.bits == 8:
        op_mr_immr(op=[0xf6], d_reg=2, target=a)
        return

def neg_(a):
    if a.bits == 64:
        op_mr_immr(op=[0xf7], d_reg=3, target=a)
        return
    if a.bits == 32:
        op_mr_immr(op=[0xf7], d_reg=3, target=a)
        return
    if a.bits == 8:
        op_mr_immr(op=[0xf6], d_reg=3, target=a)
        return

def negb_(a):
    op_mr_immr(op=[0xf6], d_reg=3, target=a)


def negl_(a):
    op_mr_immr(op=[0xf7], d_reg=3, target=a)

def notb_(a):
    op_mr_immr(op=[0xf6], d_reg=2, target=a)


def notl_(a):
    op_mr_immr(op=[0xf7], d_reg=2, target=a)


def add_(a, b):
    if type(a) is Register and is_u32(b):
        if a.bits == 64:
            logic_gate(a, b, op_eax_imm=[0x05], op_imm_=[0x81], d=0, u=u32, prefixes=[0x48])
            return
        if a.bits == 32:
            logic_gate(a, b, op_eax_imm=[0x05], op_imm_=[0x81], d=0, u=u32)
            return
        if a.bits == 8:
            logic_gate(a, b, op_eax_imm=[0x04], op_imm_=[0x80], d=0, u=u8)
            return

    op_combo(op_rm_r8=[0x00],
             op_rm_r32=[0x01],
             op_r_rm8=[0x02],
             op_r_rm32=[0x03],
             op_r_imm8=[],
             op_r_imm32=[],
             a=a,
             b=b)


def addl_(a, b):
    target_bits = 32
    if type(a) is list and type(a[0]) is Register:
        target_bits = a[0].bits
    if type(a) is Register:
        target_bits = a.bits

    if target_bits == 32:
        op_mr_immr(op=[0x81], d_reg=0, target=a, imm=u32(b))
    if target_bits == 64:
        op_mr_immr(op=[0x81], d_reg=0, target=a, imm=u32(b), prefixes=[0x48])


def addb_(a, b):
    op_mr_immr(op=[0x80], d_reg=0, target=a, imm=u8(b))


def sub_(a, b):
    if type(a) is Register and (type(b) is int or type(b) is SymBits):
        if a.bits == 64:
            logic_gate(a, b, op_eax_imm=[0x2d], op_imm_=[0x81], d=5, u=u32, prefixes=[0x48])
            return
        if a.bits == 32:
            logic_gate(a, b, op_eax_imm=[0x2d], op_imm_=[0x81], d=5, u=u32)
            return
        if a.bits == 8:
            logic_gate(a, b, op_eax_imm=[0x2c], op_imm_=[0x80], d=5, u=u8)
            return

    op_combo(op_rm_r8=[0x28],
             op_rm_r32=[0x29],
             op_r_rm8=[0x2a],
             op_r_rm32=[0x2b],
             op_r_imm8=[],
             op_r_imm32=[],
             a=a,
             b=b)


def subl_(a, b):
    target_bits = 32
    if type(a) is list and type(a[0]) is Register:
        target_bits = a[0].bits
    if type(a) is Register:
        target_bits = a.bits

    if target_bits == 32:
        op_mr_immr(op=[0x81], d_reg=5, target=a, imm=u32(b))
    if target_bits == 64:
        op_mr_immr(op=[0x81], d_reg=5, target=a, imm=u32(b), prefixes=[0x48])


def subb_(a, b):
    op_mr_immr(op=[0x80], d_reg=5, target=a, imm=u8(b))


def cmp_(a, b):
    if type(a) is Register and (type(b) is int or type(b) is SymBits):
        if a.bits == 64:
            logic_gate(a, b, op_eax_imm=[0x3d], op_imm_=[0x81], d=7, u=u32, prefixes=[0x48])
            return
        if a.bits == 32:
            logic_gate(a, b, op_eax_imm=[0x3d], op_imm_=[0x81], d=7, u=u32)
            return
        if a.bits == 8:
            logic_gate(a, b, op_eax_imm=[0x3c], op_imm_=[0x80], d=7, u=u8)
            return

    op_combo(op_rm_r8=[0x38],
             op_rm_r32=[0x39],
             op_r_rm8=[0x3a],
             op_r_rm32=[0x3b],
             op_r_imm8=[],
             op_r_imm32=[],
             a=a,
             b=b)


def cmpl_(a, b):
    target_bits = 32
    if type(a) is list and type(a[0]) is Register:
        target_bits = a[0].bits
    if type(a) is Register:
        target_bits = a.bits

    if target_bits == 32:
        op_mr_immr(op=[0x81], d_reg=7, target=a, imm=u32(b))
    if target_bits == 64:
        op_mr_immr(op=[0x81], d_reg=7, target=a, imm=u32(b), prefixes=[0x48])


def cmpb_(a, b):
    op_mr_immr(op=[0x80], d_reg=7, target=a, imm=u8(b))


def or_(a, b):
    if type(a) is Register and type(b) is int:
        if a.bits == 64:
            logic_gate(a, b, op_eax_imm=[0x0d], op_imm_=[0x81], d=1, u=u32, prefixes=[0x48])
            return
        if a.bits == 32:
            logic_gate(a, b, op_eax_imm=[0x0d], op_imm_=[0x81], d=1, u=u32)
            return
        if a.bits == 8:
            logic_gate(a, b, op_eax_imm=[0x0c], op_imm_=[0x80], d=1, u=u8)
            return

    op_combo(op_rm_r8=[0x08],
             op_rm_r32=[0x09],
             op_r_rm8=[0x0a],
             op_r_rm32=[0x0b],
             op_r_imm8=[],
             op_r_imm32=[],
             a=a,
             b=b)


def orl_(a, b):
    op_mr_immr(op=[0x81], d_reg=1, target=a, imm=u32(b))


def orb_(a, b):
    op_mr_immr(op=[0x80], d_reg=1, target=a, imm=u32(b))


def and_(a, b):
    if type(a) is Register and type(b) is int:
        if a.bits == 64:
            logic_gate(a, b, op_eax_imm=[0x25], op_imm_=[0x81], d=4, u=u32, prefixes=[0x48])
            return
        if a.bits == 32:
            logic_gate(a, b, op_eax_imm=[0x25], op_imm_=[0x81], d=4, u=u32)
            return
        if a.bits == 8:
            logic_gate(a, b, op_eax_imm=[0x24], op_imm_=[0x80], d=4, u=u8)
            return

    op_combo(op_rm_r8=[0x20],
             op_rm_r32=[0x21],
             op_r_rm8=[0x22],
             op_r_rm32=[0x23],
             op_r_imm8=[],
             op_r_imm32=[],
             a=a,
             b=b)


def andl_(a, b):
    op_mr_immr(op=[0x81], d_reg=4, target=a, imm=u32(b))


def andb_(a, b):
    op_mr_immr(op=[0x80], d_reg=4, target=a, imm=u8(b))


def xor_(a, b):
    if type(a) is Register and type(b) is int:
        if a.bits == 64:
            logic_gate(a, b, op_eax_imm=[0x35], op_imm_=[0x81], d=6, u=u32, prefixes=[0x48])
            return
        if a.bits == 32:
            logic_gate(a, b, op_eax_imm=[0x35], op_imm_=[0x81], d=6, u=u32)
            return
        if a.bits == 8:
            logic_gate(a, b, op_eax_imm=[0x34], op_imm_=[0x80], d=6, u=u8)
            return

    op_combo(op_rm_r8=[0x30],
             op_rm_r32=[0x31],
             op_r_rm8=[0x32],
             op_r_rm32=[0x33],
             op_r_imm8=[],
             op_r_imm32=[],
             a=a,
             b=b)


def xorl_(a, b):
    op_mr_immr(op=[0x81], d_reg=6, target=a, imm=u32(b))


def xorb_(a, b):
    op_mr_immr(op=[0x80], d_reg=6, target=a, imm=u32(b))

def bsr_(a, b):
    op_combo(op_r_rm32=[0x0f, 0xbd],
             a=a,
             b=b)

def ror_(a, b):
    if type(a) is Register and is_u8(b):
        if a.bits == 8:
            op_mr_immr(op=[0xc0], d_reg=1, target=a, imm=u8(b))
            return
        if a.bits == 32:
            op_mr_immr(op=[0xc1], d_reg=1, target=a, imm=u8(b))
            return
        if a.bits == 64:
            op_mr_immr(op=[0xc1], d_reg=1, target=a, imm=u8(b))
            return

    if type(a) is Register and type(b) is Register and b.bits == 8 and b.reg == 1:
        if a.bits == 8:
            op_mr_immr(op=[0xd2], d_reg=1, target=a)
            return
        if a.bits == 32:
            op_mr_immr(op=[0xd3], d_reg=1, target=a)
            return
        if a.bits == 64:
            op_mr_immr(op=[0xd3], d_reg=1, target=a)
            return

    raise MachineException('Unexpected end')


def rorl_(a, b):
    op_mr_immr(op=[0xc1], d_reg=1, target=a, imm=u8(b))


def rorb_(a, b):
    op_mr_immr(op=[0xc0], d_reg=1, target=a, imm=u8(b))


def rol_(a, b):
    if type(a) is Register and is_u8(b):
        if a.bits == 8:
            op_mr_immr(op=[0xc0], d_reg=0, target=a, imm=u8(b))
            return
        if a.bits == 32:
            op_mr_immr(op=[0xc1], d_reg=0, target=a, imm=u8(b))
            return
        if a.bits == 64:
            op_mr_immr(op=[0xc1], d_reg=0, target=a, imm=u8(b))
            return

    if type(a) is Register and type(b) is Register and b.bits == 8 and b.reg == 1:
        if a.bits == 8:
            op_mr_immr(op=[0xd2], d_reg=0, target=a)
            return
        if a.bits == 32:
            op_mr_immr(op=[0xd3], d_reg=0, target=a)
            return
        if a.bits == 64:
            op_mr_immr(op=[0xd3], d_reg=0, target=a)
            return

    raise MachineException('Unexpected end')


def roll_(a, b):
    op_mr_immr(op=[0xc1], d_reg=0, target=a, imm=u8(b))


def rolb_(a, b):
    op_mr_immr(op=[0xc0], d_reg=0, target=a, imm=u8(b))


def shl_(a, b):
    if type(a) is Register and is_u8(b):
        if a.bits == 8:
            op_mr_immr(op=[0xc0], d_reg=4, target=a, imm=u8(b))
            return
        if a.bits == 32:
            op_mr_immr(op=[0xc1], d_reg=4, target=a, imm=u8(b))
            return
        if a.bits == 64:
            op_mr_immr(op=[0xc1], d_reg=4, target=a, imm=u8(b))
            return

    if type(a) is Register and type(b) is Register and b.bits == 8 and b.reg == 1:
        if a.bits == 8:
            op_mr_immr(op=[0xd2], d_reg=4, target=a)
            return
        if a.bits == 32:
            op_mr_immr(op=[0xd3], d_reg=4, target=a)
            return
        if a.bits == 64:
            op_mr_immr(op=[0xd3], d_reg=4, target=a)
            return

    raise MachineException('Unexpected end')


def shll_(a, b):
    op_mr_immr(op=[0xc1], d_reg=4, target=a, imm=u8(b))


def shlb_(a, b):
    op_mr_immr(op=[0xc0], d_reg=4, target=a, imm=u8(b))

def sal_(a, b):
    if type(a) is Register and is_u8(b):
        if a.bits == 8:
            op_mr_immr(op=[0xc0], d_reg=4, target=a, imm=u8(b))
            return
        if a.bits == 32:
            op_mr_immr(op=[0xc1], d_reg=4, target=a, imm=u8(b))
            return
        if a.bits == 64:
            op_mr_immr(op=[0xc1], d_reg=4, target=a, imm=u8(b))
            return

    if type(a) is Register and type(b) is Register and b.bits == 8 and b.reg == 1:
        if a.bits == 8:
            op_mr_immr(op=[0xd2], d_reg=4, target=a)
            return
        if a.bits == 32:
            op_mr_immr(op=[0xd3], d_reg=4, target=a)
            return
        if a.bits == 64:
            op_mr_immr(op=[0xd3], d_reg=4, target=a)
            return

    raise MachineException('Unexpected end')


def sall_(a, b):
    op_mr_immr(op=[0xc1], d_reg=4, target=a, imm=u8(b))


def salb_(a, b):
    op_mr_immr(op=[0xc0], d_reg=4, target=a, imm=u8(b))


def shr_(a, b):
    if type(a) is Register and is_u8(b):
        if a.bits == 8:
            op_mr_immr(op=[0xc0], d_reg=5, target=a, imm=u8(b))
            return
        if a.bits == 32:
            op_mr_immr(op=[0xc1], d_reg=5, target=a, imm=u8(b))
            return
        if a.bits == 64:
            op_mr_immr(op=[0xc1], d_reg=5, target=a, imm=u8(b))
            return

    if type(a) is Register and type(b) is Register and b.bits == 8 and b.reg == 1:
        if a.bits == 8:
            op_mr_immr(op=[0xd2], d_reg=5, target=a)
            return
        if a.bits == 32:
            op_mr_immr(op=[0xd3], d_reg=5, target=a)
            return
        if a.bits == 64:
            op_mr_immr(op=[0xd3], d_reg=5, target=a)
            return

    raise MachineException('Unexpected end')


def shrl_(a, b):
    op_mr_immr(op=[0xc1], d_reg=5, target=a, imm=u8(b))


def shrb_(a, b):
    op_mr_immr(op=[0xc0], d_reg=5, target=a, imm=u8(b))

def sar_(a, b):
    if type(a) is Register and is_u8(b):
        if a.bits == 8:
            op_mr_immr(op=[0xc0], d_reg=7, target=a, imm=u8(b))
            return
        if a.bits == 32:
            op_mr_immr(op=[0xc1], d_reg=7, target=a, imm=u8(b))
            return
        if a.bits == 64:
            op_mr_immr(op=[0xc1], d_reg=7, target=a, imm=u8(b))
            return

    if type(a) is Register and type(b) is Register and b.bits == 8 and b.reg == 1:
        if a.bits == 8:
            op_mr_immr(op=[0xd2], d_reg=7, target=a)
            return
        if a.bits == 32:
            op_mr_immr(op=[0xd3], d_reg=7, target=a)
            return
        if a.bits == 64:
            op_mr_immr(op=[0xd3], d_reg=7, target=a)
            return

    raise MachineException('Unexpected end')


def sarl_(a, b):
    op_mr_immr(op=[0xc1], d_reg=7, target=a, imm=u8(b))


def sarb_(a, b):
    op_mr_immr(op=[0xc0], d_reg=7, target=a, imm=u8(b))


def call_(a):
    shift = a - (begin.buffer.cursor + 5)

    if is_i32(shift):
        op_imm(op=[0xe8], imm=i32(shift))
        return

    raise MachineException('Unexpected end')


def ret_():
    op_imm(op=[0xc3])


def jump(a, op1, op2):
    if type(a) is SymBits:
        a = a - (begin.buffer.cursor + len(op2) + 4)
        op_imm(op=op2, imm=i32(a))
        return

    shift = a - (begin.buffer.cursor + len(op1) + 1)
    if is_i8(shift):
        op_imm(op=op1, imm=i8(shift))
        return

    shift = a - (begin.buffer.cursor + len(op2) + 4)
    if is_i32(shift):
        op_imm(op=op2, imm=i32(shift))
        return


def jmp_(a):
    jump(a, [0xeb], [0xe9])


def jz_(a):
    jump(a, [0x74], [0x0f, 0x84])


def jnz_(a):
    jump(a, [0x75], [0x0f, 0x85])


def dec_(a):
    if type(a) is Register:
        op_mr_immr(op=[0xff], d_reg=1, target=a)

def inc_(a):
    if type(a) is Register:
        op_mr_immr(op=[0xff], d_reg=0, target=a)


def setnz_(a):
    if type(a) is Register and a.bits == 8:
        op_mr_immr(op=[0x0f, 0x95], d_reg=3, target=a)
        return

    raise MachineException('Unexpected end')


def setz_(a):
    if type(a) is Register and a.bits == 8:
        op_mr_immr(op=[0x0f, 0x94], d_reg=3, target=a)
        return

    raise MachineException('Unexpected end')

def setns_(a):
    if type(a) is Register and a.bits == 8:
        op_mr_immr(op=[0x0f, 0x99], d_reg=3, target=a)
        return

    raise MachineException('Unexpected end')

def sets_(a):
    if type(a) is Register and a.bits == 8:
        op_mr_immr(op=[0x0f, 0x98], d_reg=3, target=a)
        return

    raise MachineException('Unexpected end')

def setc_(a):
    if type(a) is Register and a.bits == 8:
        op_mr_immr(op=[0x0f, 0x92], d_reg=3, target=a)
        return

    raise MachineException('Unexpected end')

def setnc_(a):
    if type(a) is Register and a.bits == 8:
        op_mr_immr(op=[0x0f, 0x93], d_reg=3, target=a)
        return

    raise MachineException('Unexpected end')

def setg_(a):
    if type(a) is Register and a.bits == 8:
        op_mr_immr(op=[0x0f, 0x9f], d_reg=3, target=a)
        return

    raise MachineException('Unexpected end')

def setge_(a):
    if type(a) is Register and a.bits == 8:
        op_mr_immr(op=[0x0f, 0x9d], d_reg=3, target=a)
        return

    raise MachineException('Unexpected end')

def setl_(a):
    if type(a) is Register and a.bits == 8:
        op_mr_immr(op=[0x0f, 0x9c], d_reg=3, target=a)
        return

    raise MachineException('Unexpected end')

def setle_(a):
    if type(a) is Register and a.bits == 8:
        op_mr_immr(op=[0x0f, 0x9e], d_reg=3, target=a)
        return

    raise MachineException('Unexpected end')

def seta_(a):
    if type(a) is Register and a.bits == 8:
        op_mr_immr(op=[0x0f, 0x97], d_reg=3, target=a)
        return

    raise MachineException('Unexpected end')

def setae_(a):
    if type(a) is Register and a.bits == 8:
        op_mr_immr(op=[0x0f, 0x93], d_reg=3, target=a)
        return

    raise MachineException('Unexpected end')

def setb_(a):
    if type(a) is Register and a.bits == 8:
        op_mr_immr(op=[0x0f, 0x92], d_reg=3, target=a)
        return

    raise MachineException('Unexpected end')

def setbe_(a):
    if type(a) is Register and a.bits == 8:
        op_mr_immr(op=[0x0f, 0x96], d_reg=3, target=a)
        return

    raise MachineException('Unexpected end')

def cmovl_(a, b):
    op_mr_immr(op=[0x0f, 0x4c], d_reg=a.reg, target=b, operand_bits=a.bits)

def cmovnl_(a, b):
    op_mr_immr(op=[0x0f, 0x4d], d_reg=a.reg, target=b, operand_bits=a.bits)

def cmovz_(a, b):
    op_mr_immr(op=[0x0f, 0x44], d_reg=a.reg, target=b, operand_bits=a.bits)

def cmovnz_(a, b):
    op_mr_immr(op=[0x0f, 0x45], d_reg=a.reg, target=b, operand_bits=a.bits)

def cmovs_(a, b):
    op_mr_immr(op=[0x0f, 0x48], d_reg=a.reg, target=b, operand_bits=a.bits)

def cmovns_(a, b):
    op_mr_immr(op=[0x0f, 0x49], d_reg=a.reg, target=b, operand_bits=a.bits)

def cmovg_(a, b):
    op_mr_immr(op=[0x0f, 0x4f], d_reg=a.reg, target=b, operand_bits=a.bits)

def push_(a):
    op_mr_immr(op=[0xff], d_reg=6, target=a)

def pop_(a):
    op_mr_immr(op=[0x8f], d_reg=0, target=a)

# Float operations

def fildq_(a):
    op_mr_immr(op=[0xdf], d_reg=5, target=a)

def fldt_(a):
    op_mr_immr(op=[0xdb], d_reg=5, target=a)

def fldpi_():
    op_imm(op=[0xd9, 0xeb])

def fldcw_(a):
    op_mr_immr(op=[0xd9], d_reg=5, target=a)

def fistpq_(a):
    op_mr_immr(op=[0xdf], d_reg=7, target=a)

def fbstp_(a):
    op_mr_immr(op=[0xdf], d_reg=6, target=a)

def fstpt_(a):
    op_mr_immr(op=[0xdb], d_reg=7, target=a)

def fstp_(i):
    op_plus_r_imm(op=[0xdd, 0xd8], reg=i)

def faddp_():
    op_imm(op=[0xde, 0xc1])

def fsubp_():
    op_imm(op=[0xde, 0xe9])

def fmulp_():
    op_imm(op=[0xde, 0xc9])

def fdivp_():
    op_imm(op=[0xde, 0xf9])

def fdivrp_():
    op_imm(op=[0xde, 0xf1])

def fdiv_():
    op_imm(op=[0xde, 0xf9])

def fchs_():
    op_imm(op=[0xd9, 0xe0])

def fabs_():
    op_imm(op=[0xd9, 0xe1])

def fsin_():
    op_imm(op=[0xd9, 0xfe])

def fcos_():
    op_imm(op=[0xd9, 0xff])

def fsincos_():
    op_imm(op=[0xd9, 0xfb])

def fsqrt_():
    op_imm(op=[0xd9, 0xfa])

def st(i):
    return i

def fcomi_(i):
    op_plus_r_imm(op=[0xdb, 0xf0], reg=i)

def fcomip_(i):
    op_plus_r_imm(op=[0xdf, 0xf0], reg=i)
"""
High level compilation functions
"""


def begin(n_segments=1, segment_size=0x10000000, n_shift_factor=1):
    begin.n_segments = n_segments
    begin.segment_size = segment_size
    begin.offset = n_shift_factor * 0x10000 + align(64 + 56 * n_segments, 0x10)
    begin.buffer = Buffer(offset=begin.offset)
    begin.entry = begin.offset
    begin.symbols = defaultdict(list)


def entry():
    begin.entry = begin.buffer.cursor
    return begin.entry


def set_symbol(symbol, value=None):
    if value is None:
        value = begin.buffer.cursor

    symbol.resolved_value = value


def resolve_symbols():
    for sym_id in begin.symbols:
        for addr, sym in begin.symbols[sym_id]:
            sym.resolve()
            bs = sym.pack()
            for i in range(len(bs)):
                begin.buffer.buffer[addr + i] = bs[i]


def add_str(s):
    addr = begin.buffer.cursor
    begin.buffer.write(bytes(s, encoding='utf-8'))
    return addr


def add_bytes(bs):
    addr = begin.buffer.cursor
    begin.buffer.write(bs)
    return addr


def add_block(size):
    addr = begin.buffer.cursor
    begin.buffer.move_cursor(size)
    return addr


def set_cursor(cursor):
    begin.buffer.set_cursor(cursor)


def address():
    return begin.buffer.cursor
