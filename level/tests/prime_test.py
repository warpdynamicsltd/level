from level.core.inline2 import *
from level.execute import *
from level.tests import test_run

p = PROGRAM()


@function
def isPrime(n):
    test = U32(0)
    res = U32(0)
    k = U32(2)

    test @= (k * k <= n)
    with While(test):
        with If((n % k) == 0).Then():
            res @= 0
            ret_()
        k.add(1)
        test @= k * k <= n

    res @= 1
    return res


with p:
    n = U32(2)
    test = U32(1)
    with While(test):
        with If(isPrime(n)).Then():
            n.repr().println()
        n.add(1)
        test @= n <= 100

test_run(b'00000002\n00000003\n00000005\n00000007\n0000000b\n0000000d\n00000011\n00000013\n00000017\n0000001d\n0000001f\n00000025\n00000029\n0000002b\n0000002f\n00000035\n0000003b\n0000003d\n00000043\n00000047\n00000049\n0000004f\n00000053\n00000059\n00000061\n')