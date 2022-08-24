import os
import time

start = time.time()

import level.tests.addressing_test
import level.tests.hello_test
import level.tests.logic_gates
import level.tests.language_test

from level.tests import test_source
from level.install import *

to_be_uninstalled = False
if test_include_path() not in modules():
    to_be_uninstalled = True
    os.system(f"level install {test_include_path()}")

test_source([test_path("helloworld.lvl")], b"Hello, world!\n", b"", script=True)
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
test_source([test_path(r"math/cmpref.lvl")], b"00000001\n00000001\n")
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
test_source([test_path(r"math/eqfloat.lvl")], b"3fff:800053e2:d6238da4\n3fff:80000863:7bd05af7\n00000001\n+00000000:00000011\n00000001\n")
test_source([test_path(r"math/floorceil.lvl")],  b"3fff:800053e2:d6238da4\n3fff:80000863:7bd05af7\n00000001\n+00000000:00000014\n00000001\n")
test_source([test_path(r"math/floorceil2.lvl")],  b"+00000000:00000001\n+00000000:00000001\n+00000000:00000007\n+00000000:00000007\n-00000000:00000002\n-00000000:00000002\n+00000000:00000001\n+00000000:00000001\n")
test_source([test_path(r"math/i64tofloat.lvl")], b'+00000000:00000001\n-00000000:00000001\n')
test_source([test_path(r"math/bins.lvl")], b"00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n")
test_source([test_path(r"math/bool.lvl")], b"00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\ndynamic or\n00000001\nhello\n00000001\ndynamic and\nhello\n00000001\n00000001\n")

test_source([test_path(r"alloc.lvl")], b"07\n09\n00000001\n00000001\nend\n")
test_source([test_path(r"sbrk.lvl")], b"00000001\n00000001\n00000001\n00000001\n")

test_source([test_path(r"oop/dot.lvl")], b"+00000000:0000000a\n+00000000:00000003\n")
test_source([test_path(r"oop/add.lvl")], b"+00000000:00000034\n+00000000:00000034\n-00000000:00000004\n-00000000:00000006\n+00000000:00000004\n+00000000:00000006\n+00000000:00000001\n+00000000:00000002\n+00000000:00000003\n+00000000:00000006\n")
test_source([test_path(r"oop/sqbracket.lvl")], b"+00000000:00000002\n+00000000:00000006\n")

test_source([test_path(r"templates/simple.lvl")], b"+00000000:00000012\n+00000000:00000012\n00000000:0000000d\n+00000000:00000000\n00000001\n+00000000:00000007\n+00000000:0000000c\n")
test_source([test_path(r"templates/compound.lvl")], b"+00000000:0000000f\n+00000000:00000001\n00000002\n+00000000:00000013\n+00000000:00000007\n3fff:80000000:00000000\n00000003\n00000003\n00000003\n+00000000:00000004\n")
test_source([test_path(r"templates/type.lvl")], b"3fff:80000000:00000000\n+00000000:00000003\n4000:c0000000:00000000\n4000:c0000000:00000000\n+00000000:00000003\n+00000000:00000003\n4000:c0000000:00000000\n+00000000:00000003\n+00000000:00000003\n3fff:80000000:00000000\n4000:c0000000:00000000\n")
test_source([test_path(r"templates/nesting_type.lvl")], b"3fff:80000000:00000000\n+00000000:00000003\n4000:c0000000:00000000\n4000:c0000000:00000000\n+00000000:00000003\n+00000000:00000003\n4000:c0000000:00000000\n+00000000:00000003\n+00000000:00000003\n3fff:80000000:00000000\n4000:c0000000:00000000\n")
test_source([test_path(r"templates/nesting_type2.lvl")], b"3fff:80000000:00000000\n+00000000:00000003\n4000:c0000000:00000000\n4000:c0000000:00000000\n+00000000:00000003\n+00000000:00000003\n4000:c0000000:00000000\n+00000000:00000003\n+00000000:00000003\n3fff:80000000:00000000\n4000:c0000000:00000000\n")
test_source([test_path(r"templates/nesting_type3.lvl")], b"3fff:80000000:00000000\n+00000000:00000003\n4000:c0000000:00000000\n4000:c0000000:00000000\n+00000000:00000003\n+00000000:00000003\n4000:c0000000:00000000\n+00000000:00000003\n+00000000:00000003\n3fff:80000000:00000000\n4000:c0000000:00000000\n")
test_source([test_path(r"templates/arg_type.lvl")], b"+00000000:00000006\n00000001\n00000001\n")
test_source([test_path(r"templates/arg_type_comp.lvl")], b"+00000000:00000006\n00000001\n00000001\n")
test_source([test_path(r"templates/nesting_arg_type.lvl")], b"+00000000:00000006\n00000001\n00000001\n")
test_source([test_path(r"templates/nesting_arg_type2.lvl")], b"+00000000:00000006\n00000001\n00000001\n")
test_source([test_path(r"templates/compound2.lvl")], b"+00000000:00000004\n+00000000:00000005\n")

test_source([test_path(r"types/order.lvl")], b"+00000000:00000007\n+00000000:0000000c\n")
test_source([test_path(r"types/cast.lvl")], b"+00000000:00000003\n3fff:80000000:00000000\n+00000000:00000003\n00000001\n")
test_source([test_path(r"types/sizeof.lvl")], b"+00000000:00000003\n00000001\n+00000000:00000050\n+00000000:00000008\n00000001\n00000001\n00000001\n")

test_source([test_path(r"collections/stack_test.lvl")],
            b"stack length\n00000001\nstart pushing\nstack length\n00000001\nstart iterating\n00000001\nstart iterating\n00000001\nstart iterating\n00000001\nstart popping\nstack length\n00000001\n00000001\nstart pushing\nstack length\n00000001\nstart popping\nstack length\n00000001\n00000001\nend\n")
test_source([test_path(r"collections/stack_test_ns.lvl")],
            b"start pushing\nstart iterating\n00000001\nstart iterating\n00000001\nstart iterating\n00000001\nstart popping\n00000001\nstart pushing\nstart popping\n00000001\nend\n")
test_source([test_path(r"collections/stack_test_ns2.lvl")],
            b"start pushing\nstart iterating\n00000001\nstart iterating\n00000001\nstart iterating\n00000001\nstart popping\n00000001\nstart pushing\nstart popping\n00000001\nend\n")
test_source([test_path(r"collections/vector.lvl")], b"+00000000:00000000\n+00000000:00000001\n+00000000:00000002\n+00000000:00000003\n+00000000:00000004\n+00000000:00000005\n+00000000:00000006\n")

test_source([test_path(r"globals/simple.lvl")], b"00000001\n+00000000:00000002\n-00000000:00000002\n+00000000:00000006\n-00000000:00000002\n+00000000:00000006\nhello\n")
test_source([test_path(r"globals/expressions.lvl")], b"+00000000:00000008\n+00000000:00000004\n")
test_source([test_path(r"globals/expressions2.lvl")], b"+00000000:00000009\n+00000000:00000009\n+00000000:00000009\n+00000000:00000006\n")

test_source([test_path(r"rec/defaults.lvl")], b"+00000000:00000003\n+00000000:00000004\nend\n")
test_source([test_path(r"rec/nested.lvl")], b"+00000000:00000003\n+00000000:00000007\n+00000000:00000003\n+00000000:00000008\n+00000000:00000006\n+00000000:0000000a\nend\n")
test_source([test_path(r"ref/arithmetic.lvl")],  b"00000002\n00000003\n00000004\n00000002\n00000003\n00000004\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n")

test_source([test_path(r"allocator/describe.lvl")], b"00000001\n")
test_source([test_path(r"allocator/allocfree.lvl")], b"+00000000:00001f40\n+00000000:00000008\n00000001\n00000001\n")

test_source([test_path(r"inits/init1.lvl")], b"+00000000:00000001\n+00000000:00000002\n+00000000:00000005\n+00000000:00000008\n")
test_source([test_path(r"inits/init2.lvl")], b"+00000000:00000002\n+00000000:00000004\n+00000000:00000007\n")
test_source([test_path(r"inits/init3.lvl")], b"+00000000:00000009\nend\n")
test_source([test_path(r"inits/init4.lvl")], b"+00000000:00000002\n+00000000:00000003\n+00000000:00000007\n+00000000:00000003\n+00000000:00000005\n+00000000:00000003\n-00000000:00000001\n-00000000:00000001\n")
test_source([test_path(r"inits/init5.lvl")], b"+00000000:00000001\n+00000000:00000002\n4000:c0000000:00000000\n4001:80000000:00000000\n")

test_source([test_path(r"inheritance/simple.lvl")], b"00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n00000001\n+00000000:00000001\n+00000000:00000002\n+00000000:00000003\n+00000000:00000004\n+00000000:00000005\n3fff:80000000:00000000\n+00000000:00000011\n+00000000:00000012\n+00000000:00000013\n+00000000:00000014\n+00000000:00000015\n4000:80000000:00000000\n+00000000:00000001\n+00000000:00000002\n+00000000:00000003\n+00000000:00000004\n+00000000:00000005\n+00000000:00000006\n3fff:80000000:00000000\n+00000000:00000001\n+00000000:00000002\n+00000000:00000013\n+00000000:00000014\n+00000000:00000001\n+00000000:00000002\n3fff:80000000:00000000\nend\n")
test_source([test_path(r"inheritance/fun.lvl")], b"+00000000:00000005\n00000000:00000003\n")

# ERRORS

test_source([test_path(r"errors/nesting/nesting1.lvl")], b"", b"test:error : line 5[12]", script=True)
test_source([test_path(r"errors/nesting/nesting2.lvl")], b"", b"test:error2 : line 3[10]")
test_source([test_path(r"errors/nesting/nesting3.lvl")], b"", b"test:error : line 5[12]")



if to_be_uninstalled:
    os.system(f"level uninstall {test_include_path()}")


print("\nDone in %.2f s" % (time.time() - start))
print("All tests OK")