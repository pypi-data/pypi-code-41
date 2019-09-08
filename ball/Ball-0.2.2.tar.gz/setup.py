# -*- coding: utf-8 -*-

import re
import os
import sys
import numpy as np
from setuptools import setup, find_packages, Extension
from os import path

os_type = 'MS_WIN64' 
if sys.platform.startswith('win32'):
      py_path = sys.path
      pattern = re.compile(r'python')
      length = []
      for i in range(len(py_path)):
            temp = (py_path[i]).split("\\")
            if "Anaconda3" in temp or "anaconda3" in temp:
                length.append(len(temp))
            else:
                length.append(100)
            if pattern.match(temp[-1]):
                version = "".join(re.findall(r"\d", temp[-1]))
      if len(set(length)) == 1 and len(length) != 1:
            raise ValueError('Anaconda3 is needed!')

      ind = np.argmin(length)
      python_path = py_path[ind]
      CURRENT_DIR = os.path.dirname(__file__)
      path1 = "-I" + python_path + "\\include"
      path2 = "-L" + python_path + "\\libs"
      os.system('pre.sh ' + python_path + ' ' + version)

      cball_module = Extension('Ball._cball',
                              sources=['src/cball_wrap.c', 'src/BD.c', 'src/utilities.c', 'src/kbd.c', 'src/bcor.c', 'src/BI.c', 'src/kbcov.c'],
                              extra_compile_args=["-DNDEBUG", "-fopenmp", "-O2", "-Wall", "-std=gnu99", "-mtune=generic", "-D%s" % os_type, path1, path2],
                              extra_link_args=['-lgomp'],
                              libraries=["vcruntime140"],
                              language='c',
                              include_dirs = ["Ball"]
                              )

else:
      cball_module = Extension('Ball._cball',
                              sources=['src/cball_wrap.c', 'src/BD.c', 'src/utilities.c', 'src/kbd.c', 'src/bcor.c', 'src/BI.c', 'src/kbcov.c'],
                              extra_compile_args=["-DNDEBUG", "-fopenmp", "-O2", "-Wall", "-std=gnu99", "-mtune=generic"],
                              extra_link_args=['-lgomp'],
                              language='c',
                              include_dirs = ["Ball"]
                              )

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
      long_description = f.read()

setup(name='Ball',
      version='0.2.2',
      author="Xueqin Wang, Wenliang Pan, Heping Zhang, Hongtu Zhu, Yuan Tian, Weinan Xiao, Chengfeng Liu, Ruihuang Liu, Jin Zhu, Yanhang Zhang",
      author_email="zhangyh93@mail2.sysu.edu.cn",
      maintainer="Yanhang Zhang",
      maintainer_email="zhangyh93@mail2.sysu.edu.cn",
      description="Ball Python Package",
      long_description=long_description,
      packages=find_packages(),
      install_requires=[
            'numpy',
            'scikit-learn',
            'pygam'
      ],
      license="GPL-3",
      url="https://github.com/Mamba413/Ball",
      classifiers=[
            "Topic :: Scientific/Engineering",
            "Topic :: Scientific/Engineering :: Bio-Informatics",
            "Topic :: Scientific/Engineering :: Information Analysis",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7"
      ],
      python_requires='>=3.4',
      ext_modules=[cball_module],
      )
