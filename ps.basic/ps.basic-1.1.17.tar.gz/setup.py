from setuptools import setup, find_packages
import os


here = os.path.abspath(os.path.dirname(__file__))


def _read(name):
    def appendnl(s):
        if not s or s[-1] != '\n':
            return s + '\n'
        else:
            return s

    return appendnl(open(name).read())


VERSION = _read('VERSION.txt').strip()
version_suffix = ''
open(os.path.join(here,'src', 'ps','package_version.py'), 'w').write('version = "%s"' % VERSION)
try:
   f = open('LOCAL-VERSION') 
   version_suffix = f.readline().strip()
except IOError:
   pass

import sys

INSTALL_REQUIRES=[ 'setuptools', 'docopt' ,'pygraphviz'  ]
#INSTALL_REQUIRES=[ 'setuptools', 'docopt'   ]

setup(name='ps.basic',
      version=VERSION + version_suffix,
      description="Basic class used in PS environment",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("CHANGES.txt")).read(),
      classifiers=[
          #'Development Status :: 5 - Stable',
          'Environment :: Console',
          #'Intended Audience :: DevOps',
          'License :: Other/Proprietary License',
          'Operating System :: POSIX :: Linux',
          #'Programming Language :: Python :: 3.6 :: ',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Utilities'
      ],
      keywords='PS',
      author='Setz',
      author_email='thomas@setz.de',
      url='https://bitbucket.org/drsetz/ps.basic',
      license='',  # need/want 'ZPL'?
      use_2to3=True,
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['ps', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=INSTALL_REQUIRES ,
      entry_points={
          'console_scripts': [
              'ps_shell_log=ps.ps_shell_log:main',
          ],
      },

      )
