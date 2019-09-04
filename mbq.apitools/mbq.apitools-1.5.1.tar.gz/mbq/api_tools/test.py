from unittest.mock import patch


def _disable_authorization(test_func):
    def wrapper(*args, **kwargs):
        with patch(
            "mbq.api_tools.views.ViewFunction._perform_authorization", return_value=None
        ):
            test_func(*args, **kwargs)

    return wrapper


def disable_authorization(func_or_cls):
    if isinstance(func_or_cls, type):
        for attr in dir(func_or_cls):
            if attr.startswith("test_"):
                setattr(
                    func_or_cls,
                    attr,
                    _disable_authorization(getattr(func_or_cls, attr)),
                )
        return func_or_cls
    else:
        return _disable_authorization(func_or_cls)
