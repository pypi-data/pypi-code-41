import os
from setuptools import setup, find_packages

version = '0.0.2'
README = os.path.join(os.path.dirname(__file__), 'README.md')
long_description = open(README).read()

setup(
    name='wwu',
    version=version,
    description='Find the optimal way up to store your boxes.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Programming Language :: Python'
    ],
    keywords='boxes containers inventory permutation combinatorics',
    author='Rob Horton',
    author_email='vulgarmessiah@gmail.com',
    url='https://github.com/Um9i/wwu',
    install_requires=[

    ],
    extra_requires=[
        'pytest'
    ],
    setup_requires=['setuptools>=41.2.0'],
    download_url='https://github.com/Um9i/wwu/archive/master.zip',
    packages=find_packages(),
    include_package_data=True,
)
