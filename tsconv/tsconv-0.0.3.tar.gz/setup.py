from setuptools import setup

VERSION = '0.0.3'

setup(name='tsconv',
      version=VERSION,
      description='convert ts in sec/milisec/microsec/nanosec to human readable time',
      long_description='convert ts in sec/milisec/microsec/nanosec to human readable time',
      author='Guo Xiaoyong',
      author_email='guo.xiaoyong@gmail.com',
      url='https://github.com/guoxiaoyong/tsconv',
      install_requires=['pytz'],
      setup_requires=['pytz'],
      packages=['tsconv'],
      include_package_data=True,
      entry_points={
         'console_scripts': ['tsconv=tsconv:main'],
      },
)
