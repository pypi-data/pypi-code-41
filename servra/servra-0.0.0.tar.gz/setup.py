import setuptools


def long_description():
    with open('README.md', 'r') as file:
        return file.read()


setuptools.setup(
    name='servra',
    version='0.0.0',
    author='Michal Charemza',
    author_email='michal@charemza.name',
    description='Lightweight Python asyncio HTTP server',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/michalc/servra',
    py_modules=[
        'servra',
    ],
    python_requires='>=3.6.3',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: AsyncIO',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
    ],
    keywords=[
        'http/1.1',
    ],
)
