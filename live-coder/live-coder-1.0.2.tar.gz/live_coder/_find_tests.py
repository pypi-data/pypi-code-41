import ast
import sys
import unittest
import importlib

from ._test_class import TestClass

def _test_objects_in_test_suites(test_suits):
    tests = []
    for test_object in test_suits:
        if type(test_object) is unittest.suite.TestSuite:
            tests += _test_objects_in_test_suites(test_object)
        elif issubclass(type(test_object), unittest.TestCase):
            tests.append(test_object)
    return tests


def _get_test_methods(last_test_ids, project_root_path, tests_relative_path, test_pattern):
    if tests_relative_path in sys.modules:
        for test_id in last_test_ids:
            try:
                importlib.reload(sys.modules[test_id])
            except ImportError:
                continue
    test_loader = unittest.TestLoader()
    test_suites = test_loader.discover(project_root_path + tests_relative_path, top_level_dir=project_root_path, pattern=test_pattern)
    tests = _test_objects_in_test_suites(test_suites)
    return tests


def _group_same_types(test_methods):
    groups = [[]]
    for test in test_methods:
        if len(groups[-1]) == 0 or type(groups[-1][0]) == type(test):
            groups[-1].append(test)
        else:
            groups.append([test])
    return groups


def _raise_error(test_methods):
    if test_methods and hasattr(test_methods[0], '_exception'):
        raise test_methods[0]._exception


def find_test_classes(last_test_ids, project_root_path, tests_relative_path, test_pattern):
    '''
       Get TestClass objects for project.
    '''
    test_methods = _get_test_methods(last_test_ids, project_root_path, tests_relative_path, test_pattern)
    _raise_error(test_methods)
    test_methods_foreach_test_class = _group_same_types(test_methods)
    test_classes = [TestClass(methods) for methods in test_methods_foreach_test_class]
    return test_classes
