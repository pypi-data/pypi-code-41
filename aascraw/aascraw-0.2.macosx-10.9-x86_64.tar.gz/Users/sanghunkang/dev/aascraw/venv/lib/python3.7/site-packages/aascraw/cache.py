import json, os

class Cache():
    def __init__(self, fpath_cache):
        self.__fpath_cache = fpath_cache
        self.__cache = []

        with open(self.__fpath_cache, "r") as f:
            try:
                self.__cache = json.loads(f.read())
            except:
                pass
        # print(self.__cache)

    def add(self, action_taken, page):
        self.__cache.append([action_taken, page])

    def save(self):
        with open(self.__fpath_cache, "w") as f:
            f.write(json.dumps(self.__cache, ensure_ascii=False))

    def get(self):
        index = 0
        return self.__cache[index][0], self.__cache[index][1]