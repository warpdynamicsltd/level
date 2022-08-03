from level.core.inline2 import *
from level.tests import test_run

p = PROGRAM()

@function
def f(a):
    z = U32(1)
    z @= z + a

    return z

@function
def echo():
    y = U32(0x1)
    z = U32(0x2)
    y @= y + f(z)
    y @= y + 1
    return y + f(y)

@function
def main():
    x = U32(1)
    y = echo()
    y.repr().println()
    z = U32(2)
    x @= x + 3
    z @= x + 5
    echo()
    x.repr().print()


with p:
    main()

test_run(b'0000000b\n00000004')
