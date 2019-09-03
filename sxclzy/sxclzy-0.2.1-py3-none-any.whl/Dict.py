class Dict(dict):
    """
    内置dict方法的扩展
    增加gets方法
    传入以 逗号 “,” 为分隔符的多个key组成的字符串，或者多个key组成的列表或元组或集合，返回第一个有值的key对应的value
    若需查找的key中本身有含有逗号 "," 则建议直接使用 get 方法
    意义是寻找动态json中可能存在的值

    例如：
    新建字典：
    d = Dict()
    d["a"] = 1
    d["c"] = 5
    print(d.gets("a"))  --> 1
    print(d.gets("c,b,a"))  --> 5
    print(d.gets(['d', 'c', 'b', 'a'])) --> 5

    载入已有字典：
    d1 = {"e": 11, "f": 66, "g": 99}
    d2 = Dict(d1)
    print(d2.gets("e"))     --> 11
    print(d2.gets("h,f"))   --> 66

    其他用法与内置字典一致
    """

    def __init__(self, d=None):
        super(Dict, self).__init__()
        if isinstance(d, dict):
            for key in d:
                self[key] = d.get(key)

    def gets(self, k_iter, default=None):
        if isinstance(k_iter, (list, set, tuple)):
            for key in k_iter:
                if self.get(key):
                    return self[key]
            return default
        elif isinstance(k_iter, str):
            keys = [x.strip() for x in k_iter.split(",")]
            for key in keys:
                if self.get(key):
                    return self[key]
            return default
