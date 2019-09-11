import enum


class Separator(enum.Enum):
    DOT = "."
    STAR = "*"
    L_STR = "|"


class JsonPath(object):
    __ROOT = "$"
    __SQUARE_L = "["
    __SQUARE_R = "]"

    def __init__(self, separator=Separator.DOT):
        self.separator = separator.value

    def path(self, path: str, json):
        if not path.startswith(self.__ROOT):
            raise SyntaxError("path: %s must start with '$'" % path)

        if path.count(self.__ROOT) != 1:
            raise SyntaxError("path: %s must contains one '$'" % path)

        for i in path.split(self.separator):
            if self.__ROOT in i:
                continue

            if self.__SQUARE_L in i:
                try:
                    json = self.__get(json, i.split(self.__SQUARE_L)[0])[
                        int(i[i.index(self.__SQUARE_L) + 1: i.index(self.__SQUARE_R)])]
                    continue
                except IndexError:
                    raise IndexError("list: %s index out of range, length: %d, index: %d" % (
                        self.__get(json, i.split(self.__SQUARE_L)[0]),
                        i.split(self.__SQUARE_L)[0].__len__(),
                        int(i[i.index(self.__SQUARE_L) + 1: i.index(self.__SQUARE_R)])))
                except Exception as e:
                    raise Exception(e)

            json = self.__get(json, i)

        return json

    @staticmethod
    def __get(json, key: str):
        if isinstance(json, dict):
            if key not in json.keys():
                raise Exception("json: %s have not key: %s" % (json, key))
            return json.get(key)

        if isinstance(json, list):
            return json

        raise Exception("Can't find key: %s in primary value: %s" % (key, json))


if __name__ == '__main__':
    _json_path = JsonPath()

    _json_dict = {'k': 'v'}
    print(_json_path.path("$.k", _json_dict))

    _json_list = [{'k': 'v'}]
    print(_json_path.path("$.[0].k", _json_list))

    _json_complex = {'k': [{'k': 'v'}]}
    print(_json_path.path("$.k.[0].k", _json_complex))
