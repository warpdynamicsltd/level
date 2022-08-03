from level.core.inline2 import *
from level.execute import *
from level.tests import test_run

p = PROGRAM()


@function
def f(n):
    res = U32(1)
    i = If(n == 0)
    with i.Then():
        res @= U32(1)
    with i.Else():
        res @= n * f(n - 1)

    return res


with p:
    n = U32(10)
    f(n).repr().print()

test_run(b'00375f00')