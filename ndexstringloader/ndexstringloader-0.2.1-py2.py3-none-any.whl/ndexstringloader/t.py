import sys


def gcd(m,n):
    while m%n != 0:
        oldm = m
        oldn = n

        m = oldn
        n = oldm%oldn
    return n


class Fraction:

    def __init__(self, numerator, denominator):
        self.num = numerator
        self.den = denominator


    def __str__(self):
        return str(self.num) + "/" + str(self.den)


    def __add__(self, otherfraction):
        newnumerator = self.num*otherfraction.den + self.den*otherfraction.num
        newdenominator = self.den * otherfraction.den

        common = gcd(newnumerator, newdenominator)

        return Fraction(newnumerator // common, newdenominator // common)


    def __mul__(self, otherfraction):
        newnumerator = self.num * otherfraction.num
        newdenominator = self.den * otherfraction.den

        common = gcd(newnumerator, newdenominator)

        return Fraction(newnumerator // common, newdenominator // common)


    def __truediv__(self, otherfraction):
        newnumerator = self.num * otherfraction.den
        newdenominator = self.den * otherfraction.num

        common = gcd(newnumerator, newdenominator)

        return Fraction(newnumerator // common, newdenominator // common)



    def __sub__(self, otherfraction):
        newnumerator = self.num * otherfraction.den - self.den * otherfraction.num
        newdenominator = self.den * otherfraction.den

        if newnumerator == 0:
            return 0
        common = gcd(newnumerator, newdenominator)

        return Fraction(newnumerator // common, newdenominator // common)


    def __eq__(self, otherfraction):
        firstnum = self.num * otherfraction.den
        secondnum = otherfraction.num * self.den

        return firstnum == secondnum

    def __gt__(self, otherfraction):
        firstnum = self.num * otherfraction.den
        secondnum = otherfraction.num * self.den

        return firstnum > secondnum

    def __le__(self, otherfraction):
        firstnum = self.num * otherfraction.den
        secondnum = otherfraction.num * self.den

        return firstnum < secondnum




def main(args):

    myf = Fraction(3, 5)


    #print("I ate", myf, "of the pizza")

    f1 = Fraction(1, 8)
    f2 = Fraction(2, 16)

    f3 = f1 + f2
    print(f1, "+", f2, '=', f3)

    f3 = f1 * f2
    print(f1, "*", f2, '=', f3)

    f3 = f1 / f2
    print(f1, "/", f2, '=', f3)

    f3 = f1 - f2
    print(f1, "-", f2, '=', f3)


    print(f1, ">", f2, '=', f1 > f2)
    print(f1, "<", f2, '=', f1 < f2)
    print(f1, "==", f2, '=', f1 == f2)

    from collections import namedtuple
    Car = namedtuple('Car', 'color mileage')
    print('done')

    st = 'abc'
    for a in st:
        print(a)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
