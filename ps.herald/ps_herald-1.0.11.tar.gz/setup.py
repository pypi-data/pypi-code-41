from setuptools import setup, find_packages
import os
import sys
import subprocess

install_requires= open("requirements.txt").read().split()  
VERSION = open('VERSION.txt').read().strip()

here = os.path.abspath(os.path.dirname(__file__))
open(os.path.join(here,'src', 'ps_herald','herald_package_version.py'), 'w').write('version = "%s"' % VERSION)


setup(name='ps_herald',
      version=VERSION,
      description="Monitoring in the PS environment",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join( "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
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
      url='https://bitbucket.org/drsetz/ps.herald',
      author_email='Thomas.Setz@acm.org',
      license='', # need/want 'ZPL'?
      packages=find_packages('src'),
      package_dir={'':'src'},
      include_package_data=True,
      dependency_links=[],
      zip_safe=False,
      install_requires=install_requires,
      entry_points = {
	'console_scripts': [
	'ps_neelix=ps_herald.ps_neelix:main',
	'ps_bridge=ps_herald.ps_bridge:main',
	'ps_herald=ps_herald.ps_herald:main',
	],
     },
      )
