import io
try:
    # Python 2: "file" is built-in
    file_types = file, io.IOBase
except NameError:
    # Python 3: "file" fully replased with IOBase
    file_types = (io.IOBase,)

def ensure_file_open_and_call(path_or_fp, fn, mode='r', *args, **kwargs):
    import six
    from baiji import s3

    if isinstance(path_or_fp, six.string_types):
        with s3.open(path_or_fp, mode) as f:
            return fn(f, *args, **kwargs)
    elif isinstance(path_or_fp, file_types) or (hasattr(path_or_fp, 'read') and hasattr(path_or_fp, 'seek')):
        result = fn(path_or_fp, *args, **kwargs)
        if hasattr(path_or_fp, 'flush'):
            path_or_fp.flush()
        return result
    else:
        raise ValueError('Object {} does not appear to be a path or a file like object'.format(path_or_fp))
