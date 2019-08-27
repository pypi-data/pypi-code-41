
import sys
from os.path import abspath, join, dirname, isdir

# Use the source directory to make this easy to test.  You must run 'setup.py build' after
# modifying the C++ code, but not after modifying the Python code in the kelvin directory.

path = dirname(dirname(abspath(__file__)))
sys.path.insert(0, path)

from kelvin import Builder

b = Builder(script='hello.py', include=['dynload'], exclude=['pyexpat', 'gzip'],
            dist='dist', version='1.2.3.4',
            extra=[
                'data\\test.txt',
                ('data\\test.txt', 'test1.txt')
            ],
            version_strings = {
                0x0409 : {
                    'ProductName': 'product',
                    'ProductVersion' : '1.2',
                    'FileVersion': '1.2.3',
                    'FileDescription': 'Descriptiion'
                }
            }
)
b.build()
