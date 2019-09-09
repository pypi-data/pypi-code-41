import __main__ as _main_module
from .__Config import type_level



def var_view(level = 0):
    """
    显示变量空间中的变量
    """
    n=0
    if level>=0 and level< len(type_level):
        type_list = type_level[level]
        for i in _main_module.__dict__.copy().items():
            if i[0][0] != '_' and str(type(i[1])).split("'")[1] in type_list:
                print('name:{}    type:{}'.format(i[0],str(type(i[1])).split("'")[1]))
                n+=1
            else:
                pass
        print('共有{}个变量'.format(str(n)))
    else:
        return -1






def clear_var(save = [],level = 0):
    """
    清理变量空间
    """
    n = 0
    if level>=0 and level< len(type_level):
        type_list = type_level[level]
        for i in _main_module.__dict__.copy().items():
            if i[0][0] != '_' and i[0] not in save and str(type(i[1])).split("'")[1] in type_list:
                delattr(_main_module,i[0])
                n+=1
            else:
                pass
        print('删除{}个变量'.format(str(n)))
    else:
        return -1