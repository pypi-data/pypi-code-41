import unittest
from pyjamaparty.patterns.singleton_pattern import singleton


class TestSingletonPattern(unittest.TestCase):

    def test_singleton_method_should_raise_error(self):
        raised_error = False
        try:
            @singleton
            def this_decoration_should_raise_error():
                pass
        except AssertionError as e:
            raised_error = True
        finally:
            self.assertTrue(raised_error)

    def test_singleton_class_definition(self):
        raised_error = False
        try:
            @singleton
            class __SingletonTest(object):
                pass
        except AssertionError as e:
            raised_error = True
        finally:
            self.assertFalse(raised_error)

    def test_singleton_decorator_as_a_method(self):
        class __SingletonTest(object):
            pass
        _singleton = singleton(__SingletonTest)
        self.assertIs(type(_singleton), type(object))

    def test_singleton_usage(self):
        @singleton
        class __SingletonTest(object):
            def __init__(self, data=0):
                self.data = data

            def get_data(self):
                return self.data

        instance_a = __SingletonTest(10)
        self.assertTrue(type(instance_a), type(object))
        self.assertEqual(instance_a.get_data(), 10)
        instance_a.data = 20
        self.assertEqual(instance_a.data, 20)
        self.assertEqual(instance_a.get_data(), 20)

        instance_b = __SingletonTest(101)
        self.assertTrue(type(instance_b), type(object))
        self.assertNotEqual(instance_b.data, 101)
        self.assertNotEqual(instance_b.get_data(), 101)
        self.assertEqual(instance_a.data, instance_b.data)
        self.assertEqual(instance_a.get_data(), instance_b.get_data())
