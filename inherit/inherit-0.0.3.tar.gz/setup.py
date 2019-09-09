from setuptools import setup

setup(name='inherit',
      entry_points={
        'console_scripts': [
            'inherit=inherit.inherit:main',
        ],
      },
      version='0.0.3',
      description='',
      url='https://github.com/ke-zhang-rd/inherit.git',
      author='Ke Zhang',
      author_email='kz2249@columbia.edu',
      license='MIT',
      packages=['inherit'],
      zip_safe=False)
