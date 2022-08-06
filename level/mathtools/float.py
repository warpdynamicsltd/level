import math

def log2(x):
    return math.log(x)/math.log(2)

def upper_boundary_bit(n, a):
    v = log2(n) + a * math.log(10) / math.log(2)
    return math.ceil(v)

def convert_exact10_(s):
    l = s.split('.')
    return int("".join(l)), (-len(l[-1]) if len(l) == 2 else 0)

def convert_exact10(s, a):
    n, b = convert_exact10_(s)
    return n, b + a

def float80(s, a, precision=64):
    sign_flag = 0
    if s[0] == '-':
        sign_flag = 0x8000

    n, a = convert_exact10(s, a)

    if n == 0:
        return sign_flag, 0

    n = abs(n)
    N = upper_boundary_bit(n, a)

    # we add 1 bit of precision for rounding
    A = (precision + 1) - N
    if A >= 0:
        B = 2 ** (A)
    else:
        B = 2 ** (-A)

    if a < 0:
        if A >= 0:
            R = n * B // 10 ** (-a)
        else:
            R = (n // B) // 10 ** (-a)
    else:
        if A >= 0:
            R = n * B * (10 ** a)
        else:
            R = (n * (10 ** a)) // B

    # lowest bit
    b = R & 1

    # rounding
    significand = (R >> 1) + b

    correct = precision - significand.bit_length()

    if correct >= 0:
        significand = significand << correct
    else:
        significand = significand >> -correct
    N = N - correct - 1

    if N > 0x3fff or N < -0x3fff:
        raise ValueError("Too big exponent in float80")

    exponent = sign_flag | (0x3fff + N)

    return exponent, significand