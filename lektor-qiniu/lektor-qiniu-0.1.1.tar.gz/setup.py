import ast
import io
import re

from setuptools import setup, find_packages

with io.open('README.md', 'rt', encoding="utf8") as f:
    readme = f.read()

_description_re = re.compile(r'description\s+=\s+(?P<description>.*)')

with open('lektor_qiniu.py', 'rb') as f:
    description = str(ast.literal_eval(_description_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    author='Aaron Peng',
    author_email='arstman@gmail.com',
    description=description,
    keywords='Lektor plugin for qiniu',
    license='MIT',
    long_description=readme,
    version='0.1.1',
    long_description_content_type='text/markdown',
    name='lektor-qiniu',
    packages=find_packages(),
    py_modules=['lektor_qiniu'],
    platforms='any',
    url='https://github.com/Arstman/lektor-qiniu',
    install_requires=[
        'Lektor',
        'qiniu',
        'inifile'
    ],
    classifiers=[
        'Framework :: Lektor',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points={
        'lektor.plugins': [
            'qiniu = lektor_qiniu:QiniuPlugin',
        ]
    }
)
