# import setuptools
#
# with open("README.md", "r") as fh:
#     long_description = fh.read()
#
# setuptools.setup(
#     name="yuejzDemo",
#     version="0.0.2",python3 -m pip install --user --upgrade setuptools wheel
#     author="YueJZ",
#     author_email="yuejianzhong@sensorsdata.cn",
#     description="This is my demo",
#     long_description=long_description,
#     long_description_content_type="text/markdown",
#     url="https://github.com/YueJZSensorsData/FirstDemo",
#     packages=['SADemo'],
# )
# from distutils.core import setup
#
# # 读取项目的readme介绍
# with open("README.md", "r") as fh:
#     long_description = fh.read()
#
# setup(
#     name='yuejzDemo',
#     version='0.0.6',
#     author='YueJZ',
#     author_email='yuejianzhong@sensorsdata.cn',
#     url='https://github.com/YueJZSensorsData/FirstDemo',
#     license='LICENSE',
#     packages=['SADemo'],
#     description='This is my demo',
#     long_description=long_description,
#     long_description_content_type="text/markdown",
#
# )

import setuptools

# 读取项目的readme介绍
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="yuejzDemo",# 项目名称，保证它的唯一性，不要跟已存在的包名冲突即可
    version="0.0.8",
    author="YueJZdsa", # 项目作者
    author_email="yuejianzhong@sensorsdata.cn",
    description="This is my demo", # 项目的一句话描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hylinux1024/niubiproject",# 项目地址
    packages=setuptools.find_packages(),
    # classifiers=[
    #     "Programming Language :: Python :: 3",
    #     "License :: OSI Approved :: MIT License",
    #     "Operating System :: OS Independent",
    # ],
)