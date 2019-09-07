from .main import extractor


def get(url, params=None, **kwargs):
    kwargs.setdefault('allow_redirects', True)
    return extractor('GET', url, params=params, **kwargs)

