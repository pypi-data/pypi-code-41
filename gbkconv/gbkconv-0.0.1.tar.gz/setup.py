from setuptools import setup

setup(name='gbkconv',
      version='0.0.1',
      description='Text encoding conversion',
      long_description='Text encoding conversion',
      author='Guo Xiaoyong',
      author_email='guo.xiaoyong@gmail.com',
      url='https://github.com/guoxiaoyong/gbkconv',
      packages=['gbkconv'],
      include_package_data=True,
      entry_points={
         'console_scripts': ['gbkconv=gbkconv:main'],
      },
)
