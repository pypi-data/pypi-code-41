from setuptools import setup, find_packages
import os


here = os.path.abspath(os.path.dirname(__file__))


VERSION = open('VERSION.txt').read().strip()
version_suffix = ''
open(os.path.join(here,'src', 'ps','package_version.py'), 'w').write('version = "%s"' % VERSION)

INSTALL_REQUIRES=[ 'setuptools', 'docopt' ,'pygraphviz'  ]

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
