from level.core.inline2 import *
from level.tests import test_run

p = PROGRAM()
with p:
    n = p.DATA(b'\n')
    x = U32(0)
    test = U32(1)
    s = U32(0)
    with While(test):
        x.set(x + 1)
        s.set(s + x)
        s.repr().print()
        n.print()
        test.set(x != 10)

test_run(b'00000001\n00000003\n00000006\n0000000a\n0000000f\n00000015\n0000001c\n00000024\n0000002d\n00000037\n')

p = PROGRAM()
with p:
    data = p.DATA(b'ABCD')
    data2 = p.DATA(bytes(4))
    data2.set(data)
    data2.print()

test_run(b'ABCD')

p = PROGRAM()
with p:
    with CONTEXT(p) as c:
        k = U32(0)
        s = U32(0)

        test = U32(1)
        with While(test):
            k.val = k + 1
            test.val = (k != 23)

        k.repr().print()


test_run(b'00000017')