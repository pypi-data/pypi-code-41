import os
import setuptools
# See Also:
#     https://packaging.python.org/tutorials/packaging-projects/
#     https://packaging.python.org/tutorials/distributing-packages/


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setuptools.setup(
    name='MYZ',
    version='0.2.0',
    url='http://jiaozhe.me/',
    author='Jiao Zhe',
    author_email='jiaozhe1987@163.com',
    description='A practical toolkit for Ming & Yun & Zhe.',
    long_description=read('README.rst'),
    license='BSD',
    packages=setuptools.find_packages(),
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Natural Language :: Chinese (Simplified)",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.7',
)

