
from setuptools import setup, find_packages            #这个包没有的可以pip一下

setup(
    name = "base_aios",      #这里是pip项目发布的名称
    version = "0.0.30",  #版本号，数值大的会优先被pip
    keywords = ("base", "aios", "package"),
    description = "base aios package",
    long_description="",
    license = "MIT Licence",

    url = "",     #项目相关文件地址，一般是github
    author = "",
    author_email="jian.lv@hotmail.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires=[],  #这个项目需要的第三方库
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)