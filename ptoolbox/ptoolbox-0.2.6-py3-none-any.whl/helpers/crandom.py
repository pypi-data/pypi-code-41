import random
import string


class CRandom:
    @staticmethod
    def string(len, seed=string.ascii_uppercase + string.ascii_lowercase):
        return ''.join(random.choices(seed, k=len))

    @staticmethod
    def list_int(len, vmin, vmax, distinct = False):
        if not distinct:
            res = []
            for i in range(0, len):
                res.append(CRandom.int(vmin, vmax))
            return res
        else:
            return random.sample(range(vmin, vmax+1), len)

    @staticmethod
    def int(min, max):
        return random.randint(min, max)


if __name__ == '__main__':
    print(CRandom.string(10))
    print(*CRandom.list_int(10, -10, 10, distinct=True))
    print(CRandom.int(1,10))
