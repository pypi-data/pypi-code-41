from setuptools import setup

setup(name='pyc_viewer',
      version='0.0.1',
      description='Python bytecode viewer',
      long_description='Python bytecode viewer',
      author='Guo Xiaoyong',
      author_email='guo.xiaoyong@gmail.com',
      url='https://github.com/guoxiaoyong/pyc_viewer',
      include_package_data=True,
      packages=['pyc_viewer'],
      entry_points={
         'console_scripts': ['pyc_viewer=pyc_viewer:main'],
      },
)
