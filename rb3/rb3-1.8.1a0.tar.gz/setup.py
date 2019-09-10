import re
import ast
from setuptools import setup


_version_re = re.compile(r'__version__\s+=\s+(.*)')


with open('rb/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

f = open('README.md')
try:
    README = f.read()
finally:
    f.close()

setup(
    name='rb3',
    author='Beijing ColorfulClouds Technology Co.,Ltd.',
    author_email='admin@caiyunapp.com',
    # original author: Functional Software Inc.
    # original email: hello@getsentry.com
    version=version,
    url='https://github.com/caiyunapp/rb3',
    packages=['rb'],
    description='rb3, the redis blaster which support Python 3.7',
    long_description=README,
    long_description_content_type="text/markdown",
    keywords='Redis rb python3',
    install_requires=[
        'redis>=2.6',
        'six>=1.12.0'
    ],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
    ],
)
