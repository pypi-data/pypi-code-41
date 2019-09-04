def try_to(f, *args, **kwargs):
    try:
        return f(*args, **kwargs)
    except Exception as e:
        return e


def try_or_none(f, *args, **kwargs):
    try:
        return f(*args, **kwargs)
    except:
        return
