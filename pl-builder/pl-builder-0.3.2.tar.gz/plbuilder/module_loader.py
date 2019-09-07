import importlib.util
import os
import sys


imported_modules = []


def load_module_from_file_with_reimporting(file_path: str):
    """
    Loads a module from file, but also re-executes any imports from the module
    :param file_path:
    :return:
    """
    global imported_modules
    if imported_modules:
        [sys.modules.pop(module) for module in imported_modules]
        imported_modules = []
    original_modules = list(sys.modules.keys())
    mod = _module_from_file(file_path)
    all_modules = list(sys.modules.keys())
    imported_modules = [module for module in all_modules if module not in original_modules]
    return mod


def _module_from_file(file_path: str):
    mod_name = os.path.basename(file_path).strip('.py')
    return _module_from_file_and_name(file_path, mod_name)


def _module_from_file_and_name(file_path: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod