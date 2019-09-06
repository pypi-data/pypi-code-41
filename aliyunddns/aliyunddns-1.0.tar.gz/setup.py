import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def readall(*args):
    with open(os.path.join(here, *args), encoding='utf8') as fp:
        return fp.read()


README = readall('README.md')

setup(
    name='aliyunddns',
    version='1.0',
    description='A dynamic DNS client for Aliyun written in pure Python',
    long_description=README,
    long_description_content_type="text/markdown",
    author='Gerhard Tan',
    author_email='gerhard.gh.ta@gmail.com',
    url='https://github.com/koho/aliyunddns',
    py_modules=['aliyunddns'],
    entry_points={
        "console_scripts": [
            "aliyunddns=aliyunddns:main",
        ],
    }
)
