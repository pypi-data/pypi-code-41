import importlib


class TestClass:
    def sub(self, a, b):
        return a - b

    def add(self, a, b):
        return a + b

    def echo(self):
        print ("test")

    def __str__(self):
        return str(self.__dict__)

def main():
    class_name = "TestClass"  # 类名
    module_name = "test"  # 模块名
    method = "echo"  # 方法名

    module = __import__(module_name)  # import module
    print ("#module:", module)
    c = getattr(module, class_name)
    print ("#c:", c)
    obj = c()  # new class
    print ("#obj:", obj)
    print(obj)
    obj.echo()
    mtd = getattr(obj, method)
    mtd()  # call def

    mtd_add = getattr(obj, "add")
    t = mtd_add(1, 2)
    print ("#t:", t)

    mtd_sub = getattr(obj, "sub")
    print (mtd_sub(2, 1))


TEST1="EEEE"
def TEST():
    print(str(TEST.__name__)+"1")

def print_all(obj):
    print('\n'.join(['%s:%s' % item for item in importlib.__dict__.items()]))

if __name__ == '__main__':
    print_all("")
    from poslocalbll.tools import gethardware
    print (gethardware.__all__)
