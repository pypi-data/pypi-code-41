import io
import os
from setuptools import find_packages
from setuptools import setup

requirements = {
    'install': [
        'kaldiio',
        'pandas',
        'pyyaml',
        'seaborn',
    ],
    'setup': [

    ],
    'test': [

    ],
    'doc': [

    ]
}

install_requires = requirements['install']
setup_requires = requirements['setup']
tests_require = requirements['test']
extras_require = {k: v for k, v in requirements.items()
                  if k not in ['install', 'setup']}

dirname = os.path.dirname(__file__)
setup(name='nnsp',
      version='0.1.0',
      url='',
      author='Songxiang Liu',
      author_email='songxiangliu.cuhk@gmail.com',
      description='NNSP: Neural network based end-to-end Speech Processing toolkit',
      long_description=io.open(os.path.join(dirname, 'README.md'),
                               encoding='utf-8').read(),
      license='Apache Software License',
      packages=find_packages(include=['nnsp*']),
      install_requires=install_requires,
      setup_requires=setup_requires,
      tests_require=tests_require,
      extras_require=extras_require,
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Intended Audience :: Science/Research',
          'Operating System :: POSIX :: Linux',
          'License :: OSI Approved :: Apache Software License',
          'Topic :: Software Development :: Libraries :: Python Modules'],
      )


