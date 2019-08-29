from distutils.core import setup

setup(
    name = "mathye",#对应我们模块的名字
    version = "1.0",#版本号
    description="这是第一个对外发布的模块",#描述
    author= "叶书腾",#作者
    author_email="ShutengY@163.com",
    py_modules = ["mathye.demo2","mathye.dome1"]#要发布的模块
)
