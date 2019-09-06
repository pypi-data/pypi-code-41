from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
setup(
    name='AwesomeBuild',
    description='Awesome build manager to replace Makefiles. It allows very fast building!',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='2.5.0',
    author='Raphael Jacob',
    author_email='r.jacob2002@gmail.com',
    url='https://github.com/ski7777/AwesomeBuild',
    license='GPLv3',
    packages=['AwesomeBuild'],
    install_requires=['weasyprint'],
    entry_points={
        'console_scripts': [
            'AwesomeBuild = AwesomeBuild.__main__:main'
        ]
    }
)
