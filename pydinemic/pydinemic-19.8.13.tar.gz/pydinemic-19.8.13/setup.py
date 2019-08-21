from distutils.core import setup, Extension
import os
import sys

version = os.environ.get('PYDINEMIC_VERSION')
boost_lib = None
for arch in ('arm-linux-gnueabihf', 'x86_64-linux-gnu'):
  if os.path.exists('/usr/lib/' + arch + '/libboost_python3.so'):
      boost_lib = 'boost_python3'
      break
  elif os.path.exists('/usr/lib/' + arch + '/libboost_python37.so'):
      boost_lib = 'boost_python37'
      break
  elif os.path.exists('/usr/lib/' + arch + '/libboost_python-py37.so'):
      boost_lib = 'boost_python-py37'
      break
  elif os.path.exists('/usr/lib/' + arch + '/libboost_python3-py37.so'):
      boost_lib = 'boost_python3-py37'
      break
  elif os.path.exists('/usr/lib/' + arch + '/libboost_python-py35.so'):
      boost_lib = 'boost_python-py35'
      break
  elif os.path.exists('/usr/lib/' + arch + '/libboost_python-py35.so'):
      boost_lib = 'boost_python-py35'
      break
      
if boost_lib is None:
    print('Failed to find boost::python libraries. Check in your system')
    sys.exit(1)

pydinemic = Extension('pydinemic',
                      sources=['src/pydinemic/module.cpp',
                               'src/pydinemic/pyaction.cpp',
                               'src/pydinemic/pydfield.cpp',
                               'src/pydinemic/pydlist.cpp',
                               'src/pydinemic/pydmodel.cpp'],
                      include_dirs=['/usr/include', 'src/pydinemic'],
                      library_dirs=['/usr/lib/x86_64-linux-gnu/'],
                      runtime_library_dirs=['/usr/lib/x86_64-linux-gnu/'],
                      libraries=[boost_lib, 'dinemic'])


setup(name='pydinemic',
      version='19.8.13',
      author='cloudover.io ltd.',
      description='Dinemic framework for python',
      package_dir={'': 'src'},
      packages=['pkg'],
      headers=['src/pydinemic/module.h',
               'src/pydinemic/pyaction.h',
               'src/pydinemic/pydfield.h',
               'src/pydinemic/pydlist.h',
               'src/pydinemic/pydmodel.h',
               'src/pydinemic/pyaction.h'],
      ext_modules=[pydinemic])
