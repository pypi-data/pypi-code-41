from setuptools import setup

setup(name='tsconv',
      version='0.0.1',
      description='merge multiple ssh config to one config',
      long_description='merge multiple ssh config to one config',
      author='Guo Xiaoyong',
      author_email='guo.xiaoyong@gmail.com',
      url='https://github.com/guoxiaoyong/tsconv',
      packages=['tsconv'],
      include_package_data=True,
      entry_points={
         'console_scripts': ['tsconv=tsconv:main'],
      },
)
