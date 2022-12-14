from level.core.machine_x86_64 import *
from level.tests import test

begin()
hello = "Hello, Level!\n"
text = add_str(hello)
entry()
mov_(edx, len(hello))
mov_(ecx, text)
mov_(ebx, 1)
mov_(eax, 4)
int_(0x80)
mov_(eax, 1)
mov_(ebx, 0)
int_(0x80)

test(b'Hello, Level!\n\xba\x0e\x00\x00\x00\xb9\x80\x00\x01\x00\xbb\x01\x00\x00\x00\xb8\x04\x00\x00\x00\xcd\x80\xb8\x01\x00\x00\x00\xbb\x00\x00\x00\x00\xcd\x80')

begin()
array = add_bytes(b"0123456789abcdef")
text = add_bytes(b"\x00\x00\x00")
entry()
mov_(al, 0x23)
mov_(ebx, 0)
mov_(bl, al)
and_(bl, 0xf)
mov_(bl, [ebx + array])
mov_([text + 1], bl)
ror_(al, 4)
mov_(bl, al)
mov_(bl, [ebx + array])
mov_([text], bl)
mov_(edx, 3)
mov_(ecx, text)
mov_(ebx, 1)
mov_(eax, 4)
int_(0x80)
mov_(eax, 1)
mov_(ebx, 0)
int_(0x80)

test(b'0123456789abcdef\x00\x00\x00\xb0#\xbb\x00\x00\x00\x00\x88\xc3\x80\xe3\x0f\x8a\x1c\x1d\x80\x00\x01\x00\x88\x1c%\x91\x00\x01\x00\xc0\xc8\x04\x88\xc3\x8a\x1c\x1d\x80\x00\x01\x00\x88\x1c%\x90\x00\x01\x00\xba\x03\x00\x00\x00\xb9\x90\x00\x01\x00\xbb\x01\x00\x00\x00\xb8\x04\x00\x00\x00\xcd\x80\xb8\x01\x00\x00\x00\xbb\x00\x00\x00\x00\xcd\x80')