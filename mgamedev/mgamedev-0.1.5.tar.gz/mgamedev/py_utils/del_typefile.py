# encoding:utf8

'''删除某一个类型的文件'''

import os

def iter_public(path, typename):
    for filename in os.listdir(path):
        fileobj = os.path.join(path, filename)
        if os.path.isfile(fileobj):
            if filename.endswith(typename):
                os.remove(fileobj)
                print ("Del the file-->>%s" % fileobj)
        else:
            iter_public(fileobj, typename)