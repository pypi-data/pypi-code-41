import unittest
from datetime import datetime, timedelta
from time import sleep, time
import cache_function as cache_function_module
from cache_function import cache_function


class DummyCache:
    class Entry(object):
        pass

    def __init__(self):
        self.cache = dict()

    def get(self, key, default=None):
        obj = self.cache.get(key, default)
        if not obj:
            return None
        if obj.end_time < datetime.now():
            self.cache[key] = None
            return None
        return obj.value

    def set(self, key, value, expiry):
        obj = DummyCache.Entry()
        obj.key = key
        obj.value = value
        obj.end_time = datetime.now() + timedelta(seconds=expiry)
        self.cache[key] = obj

    def clear(self):
        self.cache.clear()


cache = DummyCache()

cache_function_module.cache = cache


# This decorator is to fetch the result of the function and the time elapsed to run it
def time_function(func):
    def with_time(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        end = time()
        return result, end - start

    return with_time


# This decorator is to test multiple decorator scenarios
def logged(func):
    def with_logging(*args, **kwargs):
        print("this is the logging " + func.__name__ + " was called")
        return func(*args, **kwargs)

    return with_logging


def factorial(n):
    if n < 0:
        raise Exception("Invalid Input")
    return 1 if n < 2 else n * factorial(n - 1)


class MyTestCase(unittest.TestCase):

    def setUp(self):
        def add_factorial(a, b, c):
            return factorial(a) + factorial(b) + factorial(c)

        self.add_factorial = add_factorial

    def test_cache(self):
        @time_function
        @cache_function
        def add_factorial0(a, b, c):
            sleep(1)
            return self.add_factorial(a, b, c)

        cache.clear()

        first_hit1 = add_factorial0(1, 2, 3)
        second_hit1 = add_factorial0(1, 2, 3)
        first_hit2 = add_factorial0(1, 2, 4)
        second_hit2 = add_factorial0(1, 2, 4)

        assert (first_hit1[0] == 9)
        assert (second_hit1[0] == 9)
        assert (first_hit1[1] > 1.0)
        assert (second_hit1[1] < 0.1)
        assert (first_hit2[0] == 27)
        assert (second_hit2[0] == 27)
        assert (first_hit2[1] > 1.0)
        assert (second_hit2[1] < 0.1)

    def test_multiple_annotation_syntax(self):
        @logged
        @cache_function(expiry=2)
        def add_factorial1(a, b, c, *args, **kwargs):
            return self.add_factorial(a, b, c)

        @logged
        @cache_function(2)
        def add_factorial2(a, b, c, *args, **kwargs):
            return self.add_factorial(a, b, c)

        @logged
        @cache_function()
        def add_factorial3(a, b, c, *args, **kwargs):
            return self.add_factorial(a, b, c)

        @cache_function()
        @logged
        def add_factorial4(a, b, c, *args, **kwargs):
            return self.add_factorial(a, b, c)

        @cache_function
        @logged
        def add_factorial5(a, b, c, *args, **kwargs):
            return self.add_factorial(a, b, c)

        @logged
        @cache_function
        def add_factorial6(a, b, c, *args, **kwargs):
            return self.add_factorial(a, b, c)

        cache.clear()
        assert (add_factorial1(1, 2, 3) == 9)
        cache.clear()
        assert (add_factorial2(1, 2, 3) == 9)
        cache.clear()
        assert (add_factorial3(1, 2, 3) == 9)
        cache.clear()
        assert (add_factorial4(1, 2, 3) == 9)
        cache.clear()
        assert (add_factorial5(1, 2, 3) == 9)
        cache.clear()
        assert (add_factorial6(1, 2, 3) == 9)
        cache.clear()
        assert (add_factorial6(1, 2, 3, 4, 5, 6) == 9)
        cache.clear()
        assert (add_factorial6(1, 2, d=5, c=3) == 9)

    def test_invalid_arguments(self):
        @logged
        @cache_function
        def add_factorial7(a, b, c, *args):
            return self.add_factorial(a, b, c)

        @logged
        @cache_function
        def add_factorial8(a, b, c, **kwargs):
            return self.add_factorial(a, b, c)

        @logged
        @cache_function
        def add_factorial9(a, b, c):
            return self.add_factorial(a, b, c)

        cache.clear()
        assert (add_factorial7(1, 2, 3) == 9)
        cache.clear()
        assert (add_factorial7(1, 2, 3, 4, 5, 6) == 9)
        cache.clear()
        assert (add_factorial8(1, 2, 3, d=4, e=5) == 9)
        cache.clear()
        assert (add_factorial9(1, 2, 3) == 9)
        cache.clear()
        assert (add_factorial9(1, 2, c=3) == 9)

        with self.assertRaises(TypeError) as context:
            cache.clear()
            add_factorial7(1, 2, 3, d=4)
        with self.assertRaises(TypeError) as context:
            cache.clear()
            add_factorial8(1, 2, 3, 4)
        with self.assertRaises(TypeError) as context:
            cache.clear()
            add_factorial9(1, 2, 3, c=4)
        with self.assertRaises(TypeError) as context:
            cache.clear()
            add_factorial9(1, 2, 3, c=4)


if __name__ == '__main__':
    unittest.main()