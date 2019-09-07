from setuptools import setup, Extension

sugar_yespower_module = Extension('sugar_yespower',
                            sources = ['yespower-module.c',
                                       'yespower.c',
                                       'yespower-opt.c',
                                       'sha256.c'
                                       ],
                            extra_compile_args=['-O2', '-funroll-loops', '-fomit-frame-pointer'],
                            include_dirs=['.'])

setup (name = 'sugar_yespower',
       version = '1.0.1',
       author_email = 'yuto_tetuota@yahoo.co.jp',
       author = 'y-chan',
       url = 'https://github.com/sugarchain-dev/sugar_yespower_python3',
       description = 'Bindings for yespower-1.0 proof of work used by sugarchain',
       ext_modules = [sugar_yespower_module])
