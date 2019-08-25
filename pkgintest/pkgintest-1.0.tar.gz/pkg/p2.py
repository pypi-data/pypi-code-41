
def p2_fun():
    print("p2的函数")

#包内引用
from . import  p1
p1.p1_fun()