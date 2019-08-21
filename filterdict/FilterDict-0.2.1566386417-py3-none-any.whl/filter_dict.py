import inspect


def filter_dict(dict_to_filter, keywords, default=None):
    new_dict = {key: dict_to_filter.get(key, default) for key in keywords}
    return new_dict


def get_method_keywords(method, return_contains_args_kwargs=True):
    sig = inspect.signature(method)
    filter_keys = [
        param.name
        for param in sig.parameters.values()
        if param.kind == param.POSITIONAL_OR_KEYWORD or param.kind == param.KEYWORD_ONLY
    ]
    if not return_contains_args_kwargs:
        return filter_keys
    return (
        filter_keys,
        len(
            [
                param.name
                for param in sig.parameters.values()
                if param.kind == param.VAR_POSITIONAL
            ]
        )
        > 0,
        len(
            [
                param.name
                for param in sig.parameters.values()
                if param.kind == param.VAR_KEYWORD
            ]
        )
        > 0,
    )


def call_method(target, args=None, kwargs=None):
    if kwargs is None:
        kwargs = {}
    if args is None:
        args = []

    target_keywords, with_args, with_kwargs = get_method_keywords(target)
    if with_kwargs:
        target_dict = dict.fromkeys(target_keywords, None)
        target_dict.update(kwargs)
    else:
        target_dict = filter_dict(dict_to_filter=kwargs, keywords=target_keywords)
    return target(**target_dict)


if __name__ == "__main__":

    def f(a, b=None, **kwargs):
        print(a, b, kwargs)

    kwargs = {"a": 0, "b": 1, "c": 2}

    target_keywords, with_args, with_kwargs = get_method_keywords(f)

    print(target_keywords, with_args, with_kwargs)
    print(filter_dict(dict_to_filter=kwargs, keywords=target_keywords))
    call_method(f, **kwargs)
