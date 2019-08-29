from ECCArithmetic.ec import *
import random

x = 7889
curve = EC(0, 5, 2, 23981)

Q = curve.pickPoint()
O = ECPt.identity()

print(curve.isPointOnEC([14967, 14215]))

G = curve.pickGenerator()

y = random.randint(1, 23981)

X = x * G

Y = y * G

print(X, Y)

c = random.randint(1, 23981)

z = y + c * x

print(z)

val1 = z * G - c * X

print(val1, Y)
