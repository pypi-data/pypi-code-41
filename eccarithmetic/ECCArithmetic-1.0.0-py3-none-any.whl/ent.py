from math import log, sqrt
from random import randrange


def gcd(a, b):
    if a < 0:
        a = -a
    if b < 0:
        b = -b
    if a == 0:
        return b
    if b == 0:
        return a
    while b != 0:
        (a, b) = (b, a % b)
    return a


def primes(n):
    if n <= 1:
        return []
    X = [i for i in range(3, n + 1) if i % 2 != 0]  # (1)
    P = [2]  # (2)
    sqrt_n = sqrt(n)  # (3)
    while len(X) > 0 and X[0] <= sqrt_n:  # (4)
        p = X[0]  # (5)
        P.append(p)  # (6)
        X = [a for a in X if a % p != 0]  # (7)
    return P + X  # (8)


def trial_division(n, bound=None):
    if n == 1:
        return 1
    for p in [2, 3, 5]:
        if n % p == 0:
            return p
    if bound is None:
        bound = n
    dif = [6, 4, 2, 4, 2, 4, 6, 2]
    m = 7
    i = 1
    while m <= bound and m * m <= n:
        if n % m == 0:
            return m
        m += dif[i % 8]
        i += 1
    return n


def factor(n):
    if n in [-1, 0, 1]:
        return []
    if n < 0:
        n = -n
    F = []
    while n != 1:
        p = trial_division(n)
        e = 1
        n /= p
        while n % p == 0:
            e += 1
            n /= p
        F.append((p, e))
    F.sort()
    return F


def is_squarefree(n):
    """
    Returns True if and only if n is not divisible by the square of an integer > 1.
    """
    if n == 0:
        return False
    for p, r in factor(n):
        if r > 1:
            return False
    return True


def xgcd(a, b):
    prevx, x = 1, 0
    prevy, y = 0, 1
    while b:
        q, r = divmod(a, b)
        x, prevx = prevx - q * x, x
        y, prevy = prevy - q * y, y
        a, b = b, r
    return a, prevx, prevy


def inversemod(a, n):
    g, x, y = xgcd(a, n)
    if g != 1:
        raise ZeroDivisionError(a, n)
    assert g == 1, "a must be coprime to n."
    return x % n


def solve_linear(a, b, n):
    g, c, _ = xgcd(a, n)  # (1)
    if b % g != 0:
        return None
    return ((b / g) * c) % n


def crt(a, b, m, n):
    g, c, _ = xgcd(m, n)
    assert g == 1, "m and n must be coprime."
    return (a + (b - a) * c * m) % (m * n)


def powermod(a, m, n):
    assert m >= 0, "m must be nonnegative."  # (1)
    assert n >= 1, "n must be positive."  # (2)
    ans = 1
    apow = a
    while m != 0:
        if m % 2 != 0:
            ans = (ans * apow) % n  # (3)
        apow = (apow * apow) % n  # (4)
        m = int(m / 2)
    return ans % n


def primitive_root(p):
    if p == 2:
        return 1
    F = factor(p - 1)
    a = 2
    while a < p:
        generates = True
        for q, _ in F:
            if powermod(a, (p - 1) / q, p) == 1:
                generates = False
                break
        if generates: return a
        a += 1
    assert False, "p must be prime."


def is_pseudoprime(n, bases=[2, 3, 5, 7]):
    if n < 0: n = -n
    if n <= 1: return False
    for b in bases:
        if b % n != 0 and powermod(b, n - 1, n) != 1:
            return False
    return True


def miller_rabin(n, num_trials=4):
    some_minus_one = False
    if n < 0:
        n = -n
    if n in [2, 3]:
        return True
    if n <= 4:
        return False
    m = n - 1
    k = 0
    while m % 2 == 0:
        k += 1;
        m /= 2
    # Now n - 1 = (2**k) * m with m odd
    for i in range(num_trials):
        a = randrange(2, n - 1)  # (1)
        apow = powermod(a, m, n)
        if not (apow in [1, n - 1]):
            some_minus_one = False
            for r in range(k - 1):  # (2)
                apow = (apow ** 2) % n
                if apow == n - 1:
                    some_minus_one = True
                    break  # (3)
        if (apow in [1, n - 1]) or some_minus_one:
            prob_prime = True
        else:
            return False
    return True


def random_prime(num_digits, is_prime=miller_rabin):
    n = randrange(10 ** (num_digits - 1), 10 ** num_digits)
    if n % 2 == 0:
        n += 1
    while not is_prime(n):
        n += 2
    return n


def dh_init(p):
    n = randrange(2, p)
    return n, pow(2, n, p)


def dh_secret(p, n, mpow):
    return pow(mpow, n, p)


def str_to_numlist(s, bound):
    assert bound >= 256, "bound must be at least 256."
    n = int(log(bound) / log(256))  # (1)
    salt = min(int(n / 8) + 1, n - 1)  # (2)
    i = 0;
    v = []
    while i < len(s):  # (3)
        c = 0;
        pow = 1
        for j in range(n):  # (4)
            if j < salt:
                c += randrange(1, 256) * pow  # (5)
            else:
                if i >= len(s): break
                c += ord(s[i]) * pow  # (6)
                i += 1
            pow *= 256
        v.append(c)
    return v


def numlist_to_str(v, bound):
    assert bound >= 256, "bound must be at least 256."
    n = int(log(bound) / log(256))
    s = ""
    salt = min(int(n / 8) + 1, n - 1)
    for x in v:
        for j in range(n):
            y = x % 256
            if y > 0 and j >= salt:
                s += chr(y)
            x = int(x / 256)
    return s


def rsa_init(p, q):
    m = (p - 1) * (q - 1)
    e = 3
    while gcd(e, m) != 1: e += 1
    d = inversemod(e, m)
    return e, d, p * q


def rsa_encrypt(plain_text, e, n):
    plain = str_to_numlist(plain_text, n)
    return [powermod(x, e, n) for x in plain]


def rsa_decrypt(cipher, d, n):
    plain = [powermod(x, d, n) for x in cipher]
    return numlist_to_str(plain, n)


def legendre(a, p):
    assert p % 2 == 1, "p must be an odd prime."
    b = powermod(a, (p - 1) / 2, p)
    if b == 1:
        return 1
    elif b == p - 1:
        return -1
    return 0


def sqrtmod(a, p):
    """ Find a quadratic residue (mod p) of 'a'. p
        must be an odd prime.

        Solve the congruence of the form:
            x^2 = a (mod p)
        And returns x. Note that p - x is also a root.

        0 is returned is no square root exists for
        these a and p.

        The Tonelli-Shanks algorithm is used (except
        for some simple cases in which the solution
        is known from an identity). This algorithm
        runs in polynomial time (unless the
        generalized Riemann hypothesis is false).
    """
    # Simple cases
    #
    if legendre(a, p) != 1:
        return 0
    elif a == 0:
        return 0
    elif p == 2:
        return 0
    elif p % 4 == 3:
        return powermod(a, (p + 1) / 4, p)

    # Partition p-1 to s * 2^e for an odd s (i.e.
    # reduce all the powers of 2 from p-1)
    #
    s = p - 1
    e = 0
    while s % 2 == 0:
        s /= 2
        e += 1

    # Find some 'n' with a legendre symbol n|p = -1.
    # Shouldn't take long.
    #
    n = 2
    while legendre(n, p) != -1:
        n += 1

    # Here be dragons!
    # Read the paper "Square roots from 1; 24, 51,
    # 10 to Dan Shanks" by Ezra Brown for more
    # information
    #

    # x is a guess of the square root that gets better
    # with each iteration.
    # b is the "fudge factor" - by how much we're off
    # with the guess. The invariant x^2 = ab (mod p)
    # is maintained throughout the loop.
    # g is used for successive powers of n to update
    # both a and b
    # r is the exponent - decreases with each update
    #
    x = powermod(a, (s + 1) / 2, p)
    b = powermod(a, s, p)
    g = powermod(n, s, p)
    r = e

    while True:
        t = b
        m = 0
        for m in range(r):
            if t == 1:
                break
            t = powermod(t, 2, p)

        if m == 0:
            return x

        gs = powermod(g, 2 ** (r - m - 1), p)
        g = (gs * gs) % p
        x = (x * gs) % p
        b = (b * g) % p
        r = m


def convergents(v):
    w = [(0, 1), (1, 0)]
    for n in range(len(v)):
        pn = v[n] * w[n + 1][0] + w[n][0]
        qn = v[n] * w[n + 1][1] + w[n][1]
        w.append((pn, qn))
    del w[0]
    del w[0]
    return w


def contfrac_rat(numer, denom):
    assert denom > 0, "denom must be positive"
    a = numer
    b = denom
    v = []
    while b != 0:
        v.append(int(a / b))
        (a, b) = (b, a % b)
    return v


def contfrac_float(x):
    v = []
    w = [(0, 1), (1, 0)]  # keep track of convergents
    start = x
    while True:
        a = int(x)  # (1)
        v.append(a)
        n = len(v) - 1
        pn = v[n] * w[n + 1][0] + w[n][0]
        qn = v[n] * w[n + 1][1] + w[n][1]
        w.append((pn, qn))
        x -= a
        if abs(start - float(pn) / float(qn)) == 0:  # (2)
            del w[0];
            del w[0]  # (3)
            return v, w
        x = 1 / x


def sum_of_two_squares(n):
    assert n % 4 == 1, "p must be 1 modulo 4"
    s = dict()
    for i in range(n):
        if i * i > n:
            break
        s[i * i] = 1
        if (n - i * i) in s.keys():
            return int((n - i * i) ** (1 / 2)), i
    assert False, "Bug in sum_of_two_squares."  # (5)


def ellcurve_add(E, P1, P2):
    a, b, p = E
    assert p > 2, "p must be odd."
    if P1 == "Identity": return P2
    if P2 == "Identity": return P1
    x1, y1 = P1
    x2, y2 = P2
    x1 %= p
    y1 %= p
    x2 %= p
    y2 %= p
    if x1 == x2 and y1 == p - y2: return "Identity"
    if P1 == P2:
        if y1 == 0: return "Identity"
        lam = (3 * x1 ** 2 + a) * inversemod(2 * y1, p)
    else:
        lam = (y1 - y2) * inversemod(x1 - x2, p)
    x3 = lam ** 2 - x1 - x2
    y3 = -lam * x3 - y1 + lam * x1
    return x3 % p, y3 % p


def ellcurve_mul(E, m, P):
    assert m >= 0, "m must be nonnegative."
    power = P
    mP = "Identity"
    while m != 0:
        if m % 2 != 0:
            mP = ellcurve_add(E, mP, power)
        power = ellcurve_add(E, power, power)
        m = int(m / 2)
    return mP


def lcm_to(B):
    ans = 1
    logB = log(B)
    for p in primes(B):
        ans *= p ** int(logB / log(p))
    return ans


def pollard(N, m):
    for a in [2, 3]:
        x = powermod(a, m, N) - 1
        g = gcd(x, N)
        if g != 1 and g != N:
            return g
    return N


def randcurve(p):
    assert p > 2, "p must be > 2."
    a = randrange(p)
    while gcd(4 * a ** 3 + 27, p) != 1:
        a = randrange(p)
    return (a, 1, p), (0, 1)

##################################################
## ElGamal Elliptic Curve Cryptosystem
##################################################

def elgamal_init(p):
    E, B = randcurve(p)
    n = randrange(2, p)
    nB = ellcurve_mul(E, n, B)
    return (E, B, nB), (E, n)

def elgamal_encrypt(plain_text, public_key):
    E, B, nB = public_key
    a, b, p = E
    assert p > 10000, "p must be at least 10000."
    v = [1000 * x for x in str_to_numlist(plain_text, p / 1000)]  # (1)
    cipher = []
    for x in v:
        while not legendre(x ** 3 + a * x + b, p) == 1:  # (2)
            x = (x + 1) % p
        y = sqrtmod(x ** 3 + a * x + b, p)  # (3)
        P = (x, y)
        r = randrange(1, p)
        encrypted = (ellcurve_mul(E, r, B), ellcurve_add(E, P, ellcurve_mul(E, r, nB)))
        cipher.append(encrypted)
    return cipher


def elgamal_decrypt(cipher_text, private_key):
    E, n = private_key
    p = E[2]
    plain = []
    for rB, P_plus_rnB in cipher_text:
        nrB = ellcurve_mul(E, n, rB)
        minus_nrB = (nrB[0], -nrB[1])
        P = ellcurve_add(E, minus_nrB, P_plus_rnB)
        plain.append(P[0] / 1000)
    return numlist_to_str(plain, p / 1000)
