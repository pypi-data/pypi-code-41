# Using gmpy2.powmod may prove to be significantly faster than pow at times.

from math import gcd

def lcm(a, b):
    return a * b // gcd(a, b)

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    g, x, y = gcd(a, m)
    if g != 1:
        raise Exception('Mod inverse DNE')
    else:
        return x % m

def rsa_decrypt(c, n, d=-1, p=-1, q=-1, e=-1):
    if d > 0:
        m = pow(c, d, n)
    elif p > 0 and q > 0 and e > 0:
        lambdaN = lcm(p - 1, q - 1)
        d = modinv(e, lambdaN)
        m = pow(c, d, n)
    else:
        raise Exception('Not enough info given')

def rsa_encrypt(m, n, e):
    return pow(m, e, n)

