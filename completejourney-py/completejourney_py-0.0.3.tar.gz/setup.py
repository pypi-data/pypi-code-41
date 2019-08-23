from setuptools import setup, find_packages

from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='completejourney_py',
    version='0.0.3',
    description='Data from R package completejourney',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='James Cunningham',
    author_email='james@notbadafterall.com',
    packages=find_packages(include=['completejourney_py', 'completejourney_py.*']),
    python_requires=">=3.6.0",
    install_requires=['pandas>=0.25.0', 'pyarrow>=0.11.0'],
    setup_requires=['pytest-runner', 'flake8'],
    tests_require=['pytest'],
    package_data={'completejourney_py': ['data/*.parquet']}
)
