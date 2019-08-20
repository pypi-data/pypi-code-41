from setuptools import setup, find_packages
from haoutils import __version__, __author__


with open("README.md", encoding="utf-8") as f:
    long_text = f.read()


setup(
    name="haoutils",
    version=__version__,
    long_description=long_text,
    long_description_content_type="text/markdown",
    url="https://github.com/haoqihan/haoutils",
    author=__author__,
    author_email="2263310007@qq.com",
    license='MIT Licence',
    packages=find_packages(),
    platforms=["window10", "Linux"],
    package_data={'': ['*']},
    install_requires=['paramiko',"openpyxl"],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False
)
