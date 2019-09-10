import os
import sys
import shutil
import platform
from py_compile import compile
# 1. 先将文件编译成pyc文件:在cmd中，指定到pyc_create.py的路径下：python pyc_create compile  需要编译的文件的根路径；这样就可以将要编译的文件编译成pyc文件了，但是文件都存在各个文件夹的__pycache__中
# 2. 将__pycache__中的pyc文件拷贝到原来py存在的位置：python pyc_create copy  文件的根路径；这样就将编译的文件存在原来py文件的位置了
# 3. 将原来的py文件删掉就可以了：python pyc_create remove 文件根路径
# 4. 将文件的名字进行更改，我这里使用的是pyhon 3.5版本的，所以文件的名字变成了*.cpython-35.pyc,要将其中的cpython-35去掉，不然不能正常运行，因为文件的名字默认最后一个后缀是扩展名，其他的为文件名字
# 5. 执行完毕，就可以使用了。


class Obfuscate(object):

    def __init__(self):
        arr = platform.python_version().replace('.', '')
        self.cpython_version = 'cpython-{}'.format(arr[:2])

    def _print(self, msg):
        if self.is_debug:
            print(msg)

    def execute(self, comd, parent, cfile):
        fullname = os.path.join(parent, cfile)

        if comd == 'clean' and cfile[-4:] == '.pyc':
            try:
                os.remove(fullname)
                self._print("Success remove file:%s" % fullname)
            except:
                self._print("Can't remove file:%s" % fullname)
        # 在这里将找到的py文件进行编译成pyc，但是会指定到一个叫做__pycache__的文件夹中
        if comd == 'compile' and cfile[-3:] == '.py':
            try:
                compile(fullname)
                self._print("Success compile file:%s" % fullname)
            except:
                self._print("Can't compile file:%s" % fullname)
        if comd == 'remove' and cfile[-3:] == '.py' and cfile != 'settings.py' and cfile != 'wsgi.py':
            try:
                os.remove(fullname)
                self._print("Success remove file:%s" % fullname)
            except:
                self._print("Can't remove file:%s" % fullname)
        if comd == 'copy' and cfile[-4:] == '.pyc':
            shutil.copy(fullname, os.path.dirname(os.path.dirname(fullname)))
            self._print('update the dir of file successfully')
        if comd == 'cpython' and cfile[-4:] == '.pyc':
            cfile_name = ''
            cfile_list = cfile.split('.')
            for i in range(len(cfile_list)):
                if cfile_list[i] == self.cpython_version:
                    continue
                cfile_name += cfile_list[i]
                if i == len(cfile_list) - 1:
                    continue
                cfile_name += '.'
            shutil.move(fullname, os.path.join(parent, cfile_name))
            self._print('update the name of the file successfully')

    def run(self):
        if len(sys.argv) >= 3:
            entry = sys.argv[0]
            comd = sys.argv[1]  # 输入的命令
            path = sys.argv[2]  # 目录文件的地址
            ignorelist = []
            self.is_debug = os.getenv('is_debug')
            if len(sys.argv) >= 5 and sys.argv[3] == '--ignore':
                ignorelist = sys.argv[4:]
            if os.path.exists(path) and os.path.isdir(path):
                for parent, dirname, filename in os.walk(path):
                    if parent.replace('./', '').split('\\')[0] not in ignorelist:
                        for cfile in filter(lambda x: x != entry, filename):
                            self.execute(comd, parent, cfile)
            else:
                print("Not an directory or Direcotry doesn't exist!", path)
        else:
            print("Usage:")
            print("\tpython compile_pyc.py clean PATH\t\t#To clean all pyc files")
            print("\tpython compile_pyc.py compile PATH\t\t#To generate pyc files")
            print("\tpython compile_pyc.py remove PATH\t\t#To remove py files")


if __name__ == '__main__':
    Obfuscate().run()
