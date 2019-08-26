from functools import wraps


cache = None


def cache_function(expiry=30):
    cache_function_pattern = "cache_function_{func_module}_{func_name}_{args}_{varargs}_{kwargs}"

    def inner_function(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = get_cache_key(func, *args, **kwargs)
            print(cache_key)

            if cache_key:
                cached_data = cache.get(cache_key)
                if cached_data:
                    return cached_data

            data = func(*args, **kwargs)

            if cache_key:
                cache.set(cache_key, data, expiry)

            return data

        return wrapper

    def get_cache_key(func, *args, **kwargs):
        args_map, varargs, kwargs = validate_get_arguments(func, *args, **kwargs)

        if args_map is None or varargs is None or kwargs is None:
            return None

        return cache_function_pattern.format(func_module=func.__module__,
                                             func_name=func.func_name,
                                             args=str(args_map),
                                             varargs=str(varargs),
                                             kwargs=str(kwargs))

    # this method is to segregate the arguments into positional, varargs and kwargs to be used to make the cache key
    def validate_get_arguments(func, *varargs, **kwargs):
        varargs = list(varargs)
        kwargs = kwargs.copy()
        code = func.func_code
        args_names = code.co_varnames[:code.co_argcount]
        args_map = {}

        # this is to determine which are the actual variable argument passed in the function func in *args
        args_names_extra = args_names[len(varargs):] if len(args_names) > len(varargs) else []

        # this is to retrieve the positional arguments to the function func
        # args_names can be lesser in count to the arguments passed, because a few of them will be passed in kwargs
        args_names = args_names[:len(varargs)]

        # all the args_names we are going to assign should not be in kwargs, else it will be broken in the function call
        if any([args_name in kwargs for args_name in args_names]):
            return None, None, None
        for i in range(len(args_names)):
            args_map[args_names[i]] = varargs[i]

        # trimming the varargs to get actual varargs
        varargs = varargs[len(args_names):]

        # these extra args_name should be there in kwargs
        if any([args_name not in kwargs for args_name in args_names_extra]):
            return None, None, None
        # removing the extra args from the kwargs and assigning it to the args_name
        for args_name in args_names_extra:
            args_map[args_name] = kwargs.pop(args_name)

        return args_map, varargs, kwargs

    if not callable(expiry):
        return inner_function

    func = expiry
    expiry = 30
    return inner_function(func)
