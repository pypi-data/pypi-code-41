from typing import List, Tuple, Any
import types


class NotAwaitable:
    __slots__ = ('cls', 'name', 'explain')

    def __init__(self, cls, name: str, explain: str):
        self.cls = cls
        self.name = name
        self.explain = explain


NOT_AWAITABLES = []  # type: List[Tuple[Any, str, str]]

try:
    NOT_AWAITABLES.append((
        types.FunctionType, 'function/lambda',
        "A 'function' or 'lambda' is the result of an\n"
        "'lambda ...: ...' lambda expression or of a\n"
        "'def ...: ...' function statement.\n\n"
        "Functions can produce awaitables when called.\n\n"
        "If your function is from an 'async def ...: await'\n"
        "statement or otherwise produces an awaitable\n"
        "you must call it using '(...)' first.",
    ))
except AttributeError:
    pass

try:
    NOT_AWAITABLES.append((
        types.GeneratorType, 'generator iterator',
        "A 'generator iterator' is the result of an\n"
        "'(a for a in b)' generator expression or from\n"
        "calling a 'def ...: yield' generator function.\n\n"
        "No variant of generators is awaitable.\n\n"
        "If you are migrating from a generator-based\n"
        "framework, use 'async def ...: await' coroutines\n"
        "instead.",
    ))
except AttributeError:
    pass

try:
    NOT_AWAITABLES.append((
        types.AsyncGeneratorType, 'async generator iterator',
        "An 'async generator iterator' is the result of an\n"
        "'(await a async for a in b)' async generator or from\n"
        "calling an 'async def ...: yield' generator function.\n\n"
        "No variant of generators is awaitable.\n\n"
        "If you are migrating from a generator-based\n"
        "framework, use 'async def ...: await' coroutines\n"
        "instead.",
    ))
except AttributeError:
    pass


def help_awaitable(non_awaitable) -> str:
    base_msg = 'expected an awaitable, got %r' % non_awaitable
    for cls, name, message in NOT_AWAITABLES:
        if isinstance(non_awaitable, cls):
            return base_msg + '(%s)' % name + '\n\n' + message
