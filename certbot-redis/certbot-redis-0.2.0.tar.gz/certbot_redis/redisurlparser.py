try:
    from urllib import parse
except ImportError:
    import urlparse as parse

class RedisUrlParser:
    def __init__(self, redis_url):
        if 'redis' not in parse.uses_netloc:
            parse.uses_netloc.append('redis')

        url = parse.urlparse(redis_url)  # type: parse.ParseResult
        self._hostname = url.hostname
        self._port = url.port
        self._password = url.password
        self._key = url.path.strip('/')


    @property
    def hostname(self):
        return self._hostname


    @property
    def port(self):
        return self._port


    @property
    def password(self):
        return self._password

    @property
    def key(self):
        return self._key
