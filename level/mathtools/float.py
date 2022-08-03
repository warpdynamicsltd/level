import math

def log2(x):
    return math.log(x)/math.log(2)

def upper_bit(n, a):
    return math.floor(round(log2(n) + a * math.log(10)/math.log(2), 4))

def convert_exact10_(s):
    l = s.split('.')
    return int("".join(l)), (-len(l[-1]) if len(l) == 2 else 0)

def convert_exact10(s, a):
    n, b = convert_exact10_(s)
    return n, b + a

def float80(s, a, precision=63):
    sign_flag = 0
    if s[0] == '-':
        sign_flag = 0x8000

    n, a = convert_exact10(s, a)

    if n == 0:
        return sign_flag, 0

    # sign_flag = 0
    # if n < 0:
    #     sign_flag = 0x8000

    n = abs(n)
    N = upper_bit(n, a)

    if N > 0x3fff or N < -0x3fff:
        raise ValueError("Too big exponent in float80")

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

    #last bit
    b = R & 1

    #rounding
    significand = (R >> 1) + b

    exponent = sign_flag | (0x3fff + N)

    return exponent, significand