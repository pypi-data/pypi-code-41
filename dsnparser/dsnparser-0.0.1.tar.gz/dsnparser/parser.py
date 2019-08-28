from urllib.parse import urlparse, parse_qsl


class DsnParser(dict):
    @classmethod
    def parse(cls, dsn: str):
        rs = cls()
        url = urlparse(dsn)
        netloc = url.netloc
        rindex = netloc.rfind("(")
        if len(url.scheme) == 0:
            raise ValueError("lack db driver name")
        rs["driver"] = url.scheme
        if rindex != -1:
            if netloc[-1] != ")":
                raise ValueError("invalid netloc")
            rs["transport"] = netloc[:rindex]
            netloc = netloc[rindex+1:-1]
        else:
            rs["transport"] = "tcp"
        if ":" in netloc:
            rs["host"], rs["port"] = netloc.split(":")
            rs["port"]=int(rs["port"])
        else:
            rs["host"] = netloc
            rs["port"] = cls.default_port(rs["driver"])
        rs["database"] = url.path[1:] if url.path else ""
        rs["user"] = url.username
        rs["password"] = url.password
        pairs = parse_qsl(url.query)
        for name, value in pairs:
            rs[name] = value
        return rs

    @staticmethod
    def default_port(driver)->int:
        if driver == "mysql":
            return 3306
        return 80

    def __missing__(self, k):
        return None

    def to_pymsql(self)->dict:
        copy=self.copy()
        copy.pop("driver")
        transport=copy.pop("transport")
        if transport=="unix":
            copy["unix_socket"]=copy.pop("host")
        return copy
