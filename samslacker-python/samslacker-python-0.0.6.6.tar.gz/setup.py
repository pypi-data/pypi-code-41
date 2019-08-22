import os
from setuptools import setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name="samslacker-python",
    version="0.0.6.6",
    author="Fire In Belly Limited",
    author_email="developers@samplify.io",
    description="Python wrapper for Sam Slacker API",
    long_description_content_type="text/plain",
    license="MIT",
    keywords="",
    url="https://samplify.io",
    packages=['samslacker'],
    package_data={},
    test_suite='',
    long_description=read('README.rst'),
    install_requires=[
        'requests',
        'boto3',
    ],
    tests_require=[
    ],
    classifiers=[
    ],
)
