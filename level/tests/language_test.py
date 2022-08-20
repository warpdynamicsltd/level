from level.core.parser.code import *
from level.core.compiler.x86_64 import *
from level.tests import test_run

s = r"""
sub f(var x as int) as int{
        var y as int;
        y <- 7;
        echo x;
        return y;
    }


entry{
    var x as int;
    x <- 6;
    echo x;
    var y as int;
    y <- 3;
    x <- f(x);
    echo y;
    echo x;
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'+00000000:00000006\n+00000000:00000006\n+00000000:00000003\n+00000000:00000007\n')

s = r"""
sub g(var x as int) as int
{
    return (x + 3);
}

sub f(var x as int) as int
{
    return (2*g(x) - 6);
}

entry{
    var x as int;
    var y as int;
    y <- 2;
    if (f(1))
    {
        x <- 3*(2 + 2);
        echo(x);
    }
    else
    {
        y <- x + x;
        echo(x);
    };
    if (f(0))
    {
        x <- 3*(2 + 2);
        echo(x);
    }
    else
    {
        y <- y + x;
        echo(y);
    };
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'+00000000:0000000c\n+00000000:0000000e\n')

s = r"""
sub g(var x as int, var y as int) as int
{
    return x + y 
}

sub f(var x as int) as int
{
    return x - 1
}

entry{
    var x as int;
    var y as int;
    var z as int;

    x <- 1;
    y <- 3;
    z <- 3;

    echo y < 4;
    echo 4 < y;
    echo x < y;
    echo y < x;
    echo z < x + y;
    echo x + y < z;
    echo x + y < z + y;
    echo z + y < x + y;
    echo (f)(x) < x;
    echo x + 1 < f(x) + 1;
    echo f(x) + 1 < x + 1;
    echo f(x) + 1 < 2;
    echo 1 < 3;
    echo f(x) < f(x) + f(x);
    echo (f)(y) < (f)(y) + f(y);
    echo f(y) + f(y) < f(y);
    echo 1 < ((g))(x, y);
    echo x < g(x, y);
    echo g(x, y) < 1;
    echo g(x, y) < x;
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'00000001\n00000000\n00000001\n00000000\n00000001\n00000000\n00000001\n00000000\n00000001\n00000000\n00000001\n00000001\n00000001\n00000000\n00000001\n00000000\n00000001\n00000001\n00000000\n00000000\n')

s = r"""
sub g(var x as int, var y as int) as int
{
    return x + y 
}

sub f(var x as int) as int
{
    return x - 1
}

entry{
    var x as int;
    var y as int;
    var z as int;

    x <- 1;
    y <- 3;
    z <- 3;

    echo y >= 4;
    echo 4 >= y;
    echo x >= y;
    echo y >= x;
    echo z >= x + y;
    echo x + y >= z;
    echo x + y >= z + y;
    echo z + y >= x + y;
    echo f(x) >= x;
    echo x + 1 >= f(x) + 1;
    echo f(x) + 1 >= x + 1;
    echo f(x) + 1 >= 2;
    echo 1 >= 3;
    echo f(x) >= f(x) + f(x);
    echo f(y) >= f(y) + f(y);
    echo f(y) + f(y) >= f(y);
    echo 1 >= g(x, y);
    echo x >= g(x, y);
    echo g(x, y) >= 1;
    echo g(x, y) >= x;
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'00000000\n00000001\n00000000\n00000001\n00000000\n00000001\n00000000\n00000001\n00000000\n00000001\n00000000\n00000000\n00000000\n00000001\n00000000\n00000001\n00000000\n00000000\n00000001\n00000001\n')

s = r"""
sub g(var x as int, var y as int) as int
{
    return x + y 
}

sub f(var x as int) as int
{
    return x + 1
}

entry{
    var x as int;
    var y as int;
    var z as int;
    var k as int;

    x <- 1;
    y <- 3;
    z <- 3;
    k <- 2;


    echo y % 2;
    echo y % k;
    echo k % 2;
    echo x % 2;
    echo f(x) % 2;
    echo 2 % f(x);
    echo 2 % y;
    echo f(x) % z;
    echo 3 % 2;
    echo f(x) % f(y);
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'+00000000:00000001\n+00000000:00000001\n+00000000:00000000\n+00000000:00000001\n+00000000:00000000\n+00000000:00000000\n+00000000:00000002\n+00000000:00000002\n+00000000:00000001\n+00000000:00000002\n')

s = r"""
sub g(var x as int, var y as int) as int
{
    return x + y 
}

sub f(var x as int) as int
{
    return x + 1
}

entry{
    var x as int;
    var y as int;
    var z as int;
    var k as int;

    x <- 1;
    y <- 3;
    z <- 3;
    k <- 2;


    echo y / 2;
    echo y / k;
    echo k / 2;
    echo x / 2;
    echo f(x) / 2;
    echo 2 / f(x);
    echo 2 / y;
    echo f(x) / z;
    echo 3 / 2;
    echo f(x) / f(y)
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'+00000000:00000001\n+00000000:00000001\n+00000000:00000001\n+00000000:00000000\n+00000000:00000001\n+00000000:00000001\n+00000000:00000000\n+00000000:00000000\n+00000000:00000001\n+00000000:00000000\n')


s = """
sub is_prime(var n as int) as int
{
    var res as int;
    var k as int;
    res <- 0;
    k <- 2;
    while(k*k <= n)
    {
        if (n % k == 0)
        {
            return 0;
        }
        k <- k + 1;
    }
    return 1;
}

entry
{
    var n as int;
    n <- 2;
    while (n <= 100)
    {
        if (is_prime(n))
        {
            echo n;
        }
        n <- n + 1;
    }
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'+00000000:00000002\n+00000000:00000003\n+00000000:00000005\n+00000000:00000007\n+00000000:0000000b\n+00000000:0000000d\n+00000000:00000011\n+00000000:00000013\n+00000000:00000017\n+00000000:0000001d\n+00000000:0000001f\n+00000000:00000025\n+00000000:00000029\n+00000000:0000002b\n+00000000:0000002f\n+00000000:00000035\n+00000000:0000003b\n+00000000:0000003d\n+00000000:00000043\n+00000000:00000047\n+00000000:00000049\n+00000000:0000004f\n+00000000:00000053\n+00000000:00000059\n+00000000:00000061\n')

s = """
sub gcd(var a as int, var b as int) as int
{
    if (b == 0)
    {
        return a;
    }
    else
    {
        return gcd(b, a % b)
    }
}

# x >= y
sub _lcm(
        var x as int, 
        var y as int,
        var a as int,
        var b as int){
    var z as int;
    if (x == y)
    {
        return x;
    }
    z <- y + b;
    if (z > x)
    {
        return _lcm(z, x, b, a)
    }
    else
    {
        return _lcm(x, z, a, b)
    }
}

sub lcm(var a as int, var b as int) as int
{
    if (a > b)
    {
        return _lcm(a, b, a, b)
    }
    else
    {
        return _lcm(b, a, b, a)
    }
    
}

sub test(var a as int, var b as int) as bool
{
    return gcd(a, b) * lcm(a, b) == a * b
}

entry{
    var a as int;
    var b as int;
    a <- 1;
    var res as int;
    res <- 0;
    while (a <= 100)
    {
        b <- 1;
        while( b <= 100)
        {
            res <- res + test(a, b);
            
            b <- b + 1;
        }
        a <- a + 1;
    }
    
    echo res;
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'+00000000:00002710\n')


s = """
sub f(var x as int) as int
{
    return x + 1;
}


entry{
    var a as array(int, 3);
    a[0] <- 1;
    a[1] <- 10;
    a[2] <- a[0];
    a[0] <- a[f(0)];
    
    echo a[0];
    echo a[2];
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'+00000000:0000000a\n+00000000:00000001\n')

s = """
entry{
    var r as ref(int);
    var x as int;
    x <- 5;
    r <- ref(x);
    val(r) <- 3;
    echo x;
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'+00000000:00000003\n')

s = """
entry
{
    var k as int;   
    k <- 2;
    [{k}] <- 3;
    echo k;
    val(val(ref(ref(k)))) <- 5;
    echo k;
    val val ref ref k <- 7;
    echo k;
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'+00000000:00000003\n+00000000:00000005\n+00000000:00000007\n')

s = """
sub f{
    var r as ref(array(array(int, 10), 10));
    var i as int;
    var j as int;
    var x as int;
    
    [r][i][j] <- x;
}

entry{
    var a as array(array(int, 10), 10);
    a[3][4] <- 7;
    exec f({a}, 3, 4, 9);
    echo a[3][4];
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'+00000000:00000009\n')

s = """
sub rand as u32
{
    var seed as ref(u32);
    [seed] <- 22695477 * [seed] + 1;
    return [seed];
}

sub quick_sort{
    var r as ref(array(u32, 100));
    var start as u32;
    var len as u32;
    
    if (len < 2) {return}
    
    a $= [r];
    
    var pivot as u32;
    pivot <- a[start + len/2];
    
    var i as u32;
    var j as u32;
    var temp as u32;
    
    i <- start;
    j <- start + len - 1;
    
    while(true)
    {
        while(a[i] < pivot) {inc i}
        while(a[j] > pivot) {dec j}
        
        if (i >= j) {break}
        
        temp <- a[i];
        a[i] <- a[j];
        a[j] <- temp;
        
        inc i;
        dec j;
    }
    
    exec quick_sort({a}, start, i - start);
    exec quick_sort({a}, i, start + len - i);
}

entry{
    var a as array(u32, 100);
    var n as u32;
    var i as u32;
    
    var seed as u32;
    seed <- 13;
    
    n <- 20; 
    
    for (i <- 0; i < n; inc i)
    {
        a[i] <- rand({seed});
        echo a[i];
    }
    
    var zero as u32;
    zero <- 0;
    echo zero;
    
    exec quick_sort({a}, zero, n);
    
    
    for (i <- 0; i < n; inc i)
    {
        echo a[i];
    }
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'1195f8b2\n7666b8db\na794ff58\n3495ad39\n9cce3ace\nc708f0a7\n2fe2b494\n0cfc7aa5\n60a5aa2a\n78e906b3\n1636ed10\nbd39f451\n0aea42c6\ne27426ff\nfa93c4cc\ne245e63d\n531140a2\ncf37bd8b\n102897c8\ndaf65c69\n00000000\n0aea42c6\n0cfc7aa5\n102897c8\n1195f8b2\n1636ed10\n2fe2b494\n3495ad39\n531140a2\n60a5aa2a\n7666b8db\n78e906b3\n9cce3ace\na794ff58\nbd39f451\nc708f0a7\ncf37bd8b\ndaf65c69\ne245e63d\ne27426ff\nfa93c4cc\n')

s = """
sub f
{
    var b as array(int, 10);
    echo b[0];
}

entry{
    var a as array(int, 10);
    a[0] <- 3;
    exec f(a);
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'+00000000:00000003\n')

s = """
sub f as array(int, 10)
{
    var b as array(int, 10);
    echo b[0];
    b[0] <- 7;
    b[1] <- 5;
    return b;
}

entry{
    var a as array(int, 10);
    a[0] <- 3;
    a[1] <- 2;
    a <- f(a);
    echo a[0];
    echo a[1];
    echo f(a)[1];
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'+00000000:00000003\n+00000000:00000007\n+00000000:00000005\n+00000000:00000007\n+00000000:00000005\n')

s = """
type natural is int

type Vec3D is rec
(
    var x as int,
    var y as int,
    var z as int,
)

type Vec2D is rec
(
    var x as int,
    var y as int,
)

sub length as int
{
    var r as ref(Vec2D);
    v $= [r];
    
    return v.x * v.x + v.y * v.y;
}

sub f as int  
{
    var x as int;
    
    return x + 1;
}

entry
{
    var a as Vec3D;
    
    a.x <- 3;
    a.y <- 2;
    a.z <- 5;
    
    echo length(ref a);
    
    var r as rec(
                var x as ref(int), 
                var y as ref(int));
    
    var x as natural;
    var y as natural;
    
    x <- 3;
    y <- 7;
    
    r.x <- ref x;
    r.y <- ref y;
    
    [r.x] <- 9;
    [r.y] <- 11;
    
    echo x + y;
    echo f(y);
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'+00000000:0000000d\n+00000000:00000014\n+00000000:0000000c\n')

s = """
type exp as rec
(
    var a as array(int, 10),
    var b as array(int, 10),
)

sub f as int
{
    var r as ref(exp);
    return [r].a[0] + [r].b[0];
}

entry{
    var x as exp;
    x.a[0] <- 5;
    x.b[0] <- 4;
    echo f(ref x);
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'+00000000:00000009\n')


s = """
entry
{
    var a as int;
    var b as int;
    a <- 1;
    b <- 0;
    
    var p as bool;
    var q as bool;
    
    p <- true;
    q <- false;
    
    echo not p;
    echo not q;
    echo p and q;
    echo p or q;
    
    var r as ref(bool);
    r <- ref p;
    [r] <- false;
    echo p;
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'00000000\n00000001\n00000000\n00000001\n00000000\n')


s = """
entry
{
    var a as array(int, 10);
    var k as int;
    k <- 7;
    var r as ref(int);
    r <- ref k;
    a[4] <- 13;
    k <- 4;
    echo a[val r];
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'+00000000:0000000d\n')

s = """
entry
{
    var r as ref;
    r = "Hello, world!";
    echo r;
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'Hello, world!\n')

s = """
entry{
  var x as float;
  var k as int;
  x = -7;
  k = x;
  echo k;
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()
test_run(b'-00000000:00000007\n')

s = """
sub f(var z as float) as float
{
  return 3 * z;
}

sub g(var z as float) as float
{
  return z * 3;
}

entry{
  var x as float;
  x = 4;
  var k as int;
  k = f(x);
  echo k;
  k = g(x);
  echo k;
}
"""

entry = Parser(s).parse()
comp = Compiler(entry, StandardObjManager, CompileDriver_x86_64)
comp.compile()
test_run(b'+00000000:0000000c\n+00000000:0000000c\n')
