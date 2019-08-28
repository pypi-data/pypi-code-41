from distutils.core import setup

setup(name='ynet',
      version='1.7.2',
      description='ynet.co.il interaction library',
      long_description='A Python library that allows you to interact with comments from news articles on ynet.co.il and ynetnews.com.',
      author='sl4v',
      author_email='iamsl4v@protonmail.com',
      url='https://github.com/sl4vkek/python-ynet',
      packages=['ynet'],
      install_requires = ['requests'],
      license="WTFPL"
     )
