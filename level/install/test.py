import os

import level.tests.addressing_test
import level.tests.hello_test
import level.tests.logic_gates
import level.tests.exec_test
import level.tests.calling_test
import level.tests.recursion_test
import level.tests.factorial_test
import level.tests.prime_test
import level.tests.compiler_test
import level.tests.language_test

from level.tests import test_source
from level.install import *

to_be_uninstalled = False
if test_include_path() not in modules():
    to_be_uninstalled = True
    os.system(f"level install {test_include_path()}")

test_source([test_path("helloworld.lvl")], b"Hello, world!\n")
test_source([test_path("helloworld2.lvl")], b"Hello, world!\n")
test_source([test_path("helloworld3.lvl")], b"Hello, world!\n")
test_source([test_path("primes.lvl")], b'00000002\n00000003\n00000005\n00000007\n0000000b\n0000000d\n00000011\n00000013\n00000017\n0000001d\n0000001f\n00000025\n00000029\n0000002b\n0000002f\n00000035\n0000003b\n0000003d\n00000043\n00000047\n00000049\n0000004f\n00000053\n00000059\n00000061\n')
test_source([test_path("args.lvl"), "A", "B"], b'A\nB\n')
test_source([test_path("args2.lvl"), "A", "B"], b'A\nB\n')
test_source([test_path("args3.lvl"), "A", "B"], b'A\nB\n')

test_source([test_path(r"algo/quicksort.lvl")],  b"-6fd11e34:25010968\n+66e3ae4b:99064207\n+2a2fd32c:7a55958a\n+29a21877:eef44091\n-433f930f:3b3c3634\n-39425dd8:4d55d1d5\n+40784a6c:6f3ff3de\n-6bda719b:e8297eab\n+1f77791a:14be6840\n+3885a264:bfd7948f\n+18671417:8e3a8f72\n-6adf4318:a5c9b9a7\n-6552b9f6:e25afa0c\n-0bc8d47d:0d9e66cd\n+35c9ae02:4c3ebc46\n+6065066f:da93539d\n+5c3b65c2:c02916e8\n-4231d271:a9fa5fe9\n-75e718f7:1dccf1a6\n-488861ed:df1e52df\n+00000000:00000000\n-75e718f7:1dccf1a6\n-6fd11e34:25010968\n-6bda719b:e8297eab\n-6adf4318:a5c9b9a7\n-6552b9f6:e25afa0c\n-488861ed:df1e52df\n-433f930f:3b3c3634\n-4231d271:a9fa5fe9\n-39425dd8:4d55d1d5\n-0bc8d47d:0d9e66cd\n+18671417:8e3a8f72\n+1f77791a:14be6840\n+29a21877:eef44091\n+2a2fd32c:7a55958a\n+35c9ae02:4c3ebc46\n+3885a264:bfd7948f\n+40784a6c:6f3ff3de\n+5c3b65c2:c02916e8\n+6065066f:da93539d\n+66e3ae4b:99064207\n")

test_source([test_path(r"nesting/nesting1.lvl")], b"+00000000:00000003\n+00000000:00000004\n")
test_source([test_path(r"nesting/nesting2.lvl")], b"+00000000:00000003\n+00000000:00000004\n")
test_source([test_path(r"nesting/nesting3.lvl")], b"+00000000:00000003\n+00000000:00000004\n")
test_source([test_path(r"nesting/nesting4.lvl")], b"+00000000:00000003\n+00000000:00000004\n")
test_source([test_path(r"nesting/nesting5.lvl")], b"+00000000:00000003\n+00000000:00000004\n")
test_source([test_path(r"nesting/nesting6.lvl")], b"+00000000:00000003\n+00000000:00000004\n")
test_source([test_path(r"nesting/nesting7.lvl")], b"+00000000:00000003\n+00000000:00000004\n")
test_source([test_path(r"nesting/nesting8.lvl")], b"+00000000:00000003\n+00000000:00000004\n")
test_source([test_path(r"nesting/nesting9.lvl")], b"+00000000:00000003\n+00000000:00000004\n")
test_source([test_path(r"sub/calling.lvl")],  b"00000002\n00000003\n00000001\n00000001\n+00000000:00000005\n+00000000:00000004\n+00000000:00000006\nno-type\n+00000000:00000008\n+00000000:00000003\n")
test_source([test_path(r"math/cmpu64.lvl")], b"00000001\n")
test_source([test_path(r"math/cmpu32.lvl")], b"00000001\n")
test_source([test_path(r"math/cmpi64.lvl")], b"00000001\n")
test_source([test_path(r"math/sgni64.lvl")], b"+00000000:00000001\n+00000000:00000000\n-00000000:00000001\n")
test_source([test_path(r"math/muli64.lvl")], b"00000001\n")
test_source([test_path(r"math/divi64.lvl")], b"00000001\n")
test_source([test_path(r"math/cmpi32.lvl")], b"00000001\n")
test_source([test_path(r"math/sgni32.lvl")], b"+00000001\n+00000000\n-00000001\n")
test_source([test_path(r"math/muli32.lvl")], b"00000001\n")
test_source([test_path(r"math/divi32.lvl")], b"00000001\n")
test_source([test_path(r"math/cmpfloat.lvl")], b"00000001\n")
test_source([test_path(r"math/eqfloat.lvl")], b"3fff:800053e2:d6238da4\n3fff:80000863:7bd05af7\n00000001\n+00000000:0000000b\n00000001\n")

test_source([test_path(r"alloc.lvl")], b"07\n09\n")
test_source([test_path(r"sbrk.lvl")], b"00000001\n00000001\n00000000:0000000a\n")

test_source([test_path(r"oop/dot.lvl")], b"+00000000:0000000a\n+00000000:00000003\n")
test_source([test_path(r"oop/add.lvl")], b"+00000000:00000034\n+00000000:00000034\n-00000000:00000004\n-00000000:00000006\n+00000000:00000004\n+00000000:00000006\n+00000000:00000001\n+00000000:00000002\n")
test_source([test_path(r"oop/sqbracket.lvl")], b"+00000000:00000002\n+00000000:00000006\n")



if to_be_uninstalled:
    os.system(f"level uninstall {test_include_path()}")

print("\nAll tests OK")