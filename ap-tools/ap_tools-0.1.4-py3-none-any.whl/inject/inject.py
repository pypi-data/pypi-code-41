from functools import wraps
from typing import Sequence, Callable, Any

from .injector import Injector

def inject(*targets: Sequence[str]) -> Callable:
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            implementations = [Injector.get(target) for target in targets]
            return fn(args[0], *implementations, *args[1:], **kwargs)
        return wrapped
    return decorator
