from level.core.inline2 import *
from level.execute import *
from level.tests import test_run

p = PROGRAM()

@function
def g():
    return U32(1)

@function
def f(n):
    res = U32(0)
    with If(n != 10).Then():
        res @= f(n + g()) + g()
    return res


with p:
    a = U32(7)
    f(a).repr().println()
    a.repr().print()
    g()

test_run(b'00000003\n00000007')