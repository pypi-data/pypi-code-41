# -*- coding: utf-8 -*-

import io
import re

from setuptools import find_packages, setup
with io.open("README.txt", "rt", encoding="utf8") as f:
    readme = f.read()

with io.open("howfo/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
    name="howfo-frame",
    description="A simple example of how to layout a small site quickly",
    version=version,
    author="kalaiya86",
    author_email="kalaiya86@gmail.com",
    keywords="howfo-frame",
    url="http://www.howfo.net",
    # Name the folder where your packages live:
    # (If you have other packages (dirs) or modules (py files) then
    # put them into the package directory - they will be found
    # recursively.)

    packages=find_packages(),
    package_data={
        "": ["*.txt"],
        "howfo": ["config/*"],
    },
    include_package_data=True,
    platforms="any",
    # "package" package must contain files (see list above)
    # I called the package "package" thus cleverly confusing the whole issue...
    # This dict maps the package name =to=> directories
    # It says, package *needs* these files.
    # 通常包含与包实现相关的一些数据文件或类似于readme的文件。
    # 表示包含所有目录下的txt文件和vendor/config目录下的所有json文件
    tests_require=["pytest"],

    # 需要安装的依赖
     install_requires=[
         "flask>=1.0.2",
         "Flask-SQLAlchemy>=2.3.2",
         "Flask-Migrate>=2.5.2",
         "Flask-Script>=2.0.6"
     ],
    long_description=readme,
    # This next part it for the Cheese Shop, look a little down the page.
    # 程序的所属分类列表
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    # 此项需要，否则卸载时报windows error
    zip_safe=False
)
