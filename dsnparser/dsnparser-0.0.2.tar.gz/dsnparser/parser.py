from urllib.parse import urlparse, parse_qsl


class DsnParser(dict):
    @classmethod
    def parse(cls, dsn: str):
        rs = cls()
        url = urlparse(dsn)
        netloc = url.netloc.split("@")[-1]
        rindex = netloc.rfind("(")
        if len(url.scheme) == 0:
            raise ValueError("lack db driver name")
        rs["driver"] = url.scheme
        if rindex != -1:
            if netloc[-1] != ")":
                raise ValueError("invalid netloc ",netloc)
            rs["transport"] = netloc[:rindex]
            netloc = netloc[rindex+1:-1]
        else:
            rs["transport"] = "tcp"
        if ":" in netloc:
            print(netloc)
            rs["host"], rs["port"] = netloc.split(":")
            rs["port"] = int(rs["port"])
        else:
            rs["host"] = netloc
            rs["port"] = cls.default_port(rs["driver"])
        rs["database"] = url.path[1:] if url.path else ""
        rs["user"] = url.username if url.username is not None else ""
        rs["password"] = url.password if url.password is not None else ""
        pairs = parse_qsl(url.query)
        for name, value in pairs:
            rs[name] = value
        return rs

    @staticmethod
    def default_port(driver)->int:
        if driver == "mysql":
            return 3306
        elif driver=="redis":
            return 6379
        return 80

    def __missing__(self, k):
        return None

    def to_pymysql(self)->dict:
        copy = self.copy()
        copy.pop("driver")
        transport = copy.pop("transport")
        if transport == "unix":
            copy["unix_socket"] = copy.pop("host")
        return copy

    def to_aioredis(self)->dict:
        copy = self.copy()
        if copy["transport"] != "unix":
            scheme = copy.pop("driver")
            copy.pop("transport")
        else: 
            scheme = copy.pop("transport")
            copy.pop("driver")
        user=copy.pop("user")
        password=copy.pop("password")
        host=copy.pop("host")
        port=copy.pop("port")
        database = copy.pop("database")
        copy["address"] = f"{scheme}://{user}:{password}@{host}:{port}/{database}"
        return copy
