from gmconfig.litemerge import liteMerge


class Configuration(dict):
    def merge(self, new_object: dict) -> None:
        self.update(liteMerge(self.__dict__, new_object))
