from level.core.x86_64 import *

def m_itoa(ptr):
    code = SymBits()
    jmp_(code)
    hex_ptr = add_bytes(b"0123456789abcdef")
    set_symbol(code)
    mov_(rbx, 0)
    for i in range(8):
        mov_(bl, al)
        and_(bl, 0xf)
        mov_(bl, [ebx + hex_ptr])
        mov_([ptr + (7 - i)], bl)
        ror_(eax, 4)

def m_echo(ptr, size):
    mov_(edx, size)
    mov_(ecx, ptr)
    mov_(ebx, 1)
    mov_(eax, 4)
    int_(0x80)

def m_copy_rdi_rsi(size):
    mov_(rcx, size)
    loop = SymBits()
    set_symbol(loop)
    mov_(al, [rsi + rcx - 1])
    mov_([rdi + rcx - 1], al)
    dec_(rcx)
    jnz_(loop)

def m_exit():
    mov_(eax, 1)
    mov_(ebx, 0)
    int_(0x80)
