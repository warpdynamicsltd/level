from level.core.machine_x86_64 import *
from level.tests import test

begin()
not_(eax)

or_(eax, ebx)
or_(eax, 0x4)
or_(edx, 0x3)

and_(eax, ebx)
and_(eax, 0x4)
and_(edx, 0x3)

xor_(eax, ebx)
xor_(eax, 0x4)
xor_(edx, 0x3)

add_(eax, ebx)
add_(eax, 0x4)
add_(edx, 0x3)

test(b'\xf7\xd0\t\xd8\r\x04\x00\x00\x00\x81\xca\x03\x00\x00\x00!\xd8%\x04\x00\x00\x00\x81\xe2\x03\x00\x00\x001\xd85\x04\x00\x00\x00\x81\xf2\x03\x00\x00\x00\x01\xd8\x05\x04\x00\x00\x00\x81\xc2\x03\x00\x00\x00')


begin()
not_(al)

or_(al, bh)
or_(al, 0x4)
or_(dl, 0x3)

and_(al, dh)
and_(al, 0x4)
and_(dh, 0x3)

xor_(bl, cl)
xor_(ch, 0x4)
xor_(dh, 0x3)

add_(bl, cl)
add_(ch, 0x4)
add_(dh, 0x3)

test(b'\xf6\xd0\x08\xf8\x0c\x04\x80\xca\x03 \xf0$\x04\x80\xe6\x030\xcb\x80\xf5\x04\x80\xf6\x03\x00\xcb\x80\xc5\x04\x80\xc6\x03')