from setuptools import setup

setup(name='merge_sshconf',
      version='0.0.2',
      description='merge multiple ssh config to one config',
      long_description='merge multiple ssh config to one config',
      author='Guo Xiaoyong',
      author_email='guo.xiaoyong@gmail.com',
      url='https://github.com/guoxiaoyong/merge_sshconf',
      install_requires=['sshconf'],
      setup_requires=['sshconf'],
      packages=['merge_sshconf'],
      include_package_data=True,
      entry_points={
         'console_scripts': ['merge_sshconf=merge_sshconf:main'],
      },
)
