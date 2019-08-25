from ehelply_cacher.Cache import make_TTL
from ehelply_cacher.Cache import cached


def test_ttl():
    @cached(cache=make_TTL(0.25, maxsize=5))
    def do(num):
        print("UN CACHED: " + str(num))
        return num

    import time
    while True:
        for i in range(0, 4):
            do(i)
            time.sleep(1)


test_ttl()