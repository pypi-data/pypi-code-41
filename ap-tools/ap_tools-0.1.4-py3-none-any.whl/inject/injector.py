from typing import Callable

class Injector:
    _injectables = {}

    @staticmethod
    def add_singleton(interface: Callable, injectable: Callable):
        if interface.__name__ not in Injector._injectables:
            singleton = injectable()
            Injector._injectables[interface.__name__] = lambda: singleton

    @staticmethod
    def add_transient(interface: Callable, injectable: Callable):
        if interface.__name__ not in Injector._injectables:
            Injector._injectables[interface.__name__] = injectable

    @staticmethod
    def get(target:str):
        if target in Injector._injectables:
            return Injector._injectables[target]()
        return None
