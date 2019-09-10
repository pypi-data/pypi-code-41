class Dict2Class(object):
    """将`dict`对象转换为`class`对象

    笔记：
        1. `__getattr__`和`__setattr__`属性作用于`__init__`函数
        2. 赋值表达式不会触发`getattr`动作
    """

    def __init__(self, d):
        # print('class init:', d)
        if isinstance(d, dict):
            self._dict = d
        else:
            self._dict = {}

    def __getattr__(self, item):
        # print('get action:', item)
        return self._dict[item]

    def __setattr__(self, key, value):
        # print('set action:', key, value)
        if key == '_dict':
            object.__setattr__(self, key, value)    # 调用父类方法
        else:
            self._dict[key] = value

    def __getitem__(self, item):
        # print('get item:', item)
        return self._dict[item]

    def __setitem__(self, key, value):
        # print('set item:', key, value)
        self._dict[key] = value

    def to_dict(self):
        return self._dict
