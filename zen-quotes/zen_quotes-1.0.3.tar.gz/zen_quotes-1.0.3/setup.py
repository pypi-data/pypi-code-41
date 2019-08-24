from setuptools import setup

# install requirements of the project
with open("requirements.txt") as req:
    install_requires = req.read()

setup(
    name='zen_quotes',
    packages = ['zen_quotes'],
    version='1.0.3',
    description='A sample lib Zen of Python',
    author='Yuri Mussi',
    author_email='ymussi@gmail.com',
    license='BSD',
    url='https://github.com/ymussi/zen_quotes',
    keywords = [],
    classifiers = [],
    )