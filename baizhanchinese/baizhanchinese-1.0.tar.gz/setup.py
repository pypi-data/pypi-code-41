from distutils.core import setup
setup(
    name = "baizhanchinese",#对外我们模块的名字
    version="1.0",#版本号
    description="这是第一个对外发布的模块，咿咿呀呀，测试！！",#描述
    author="langlang",#作者
    author_email="1643655064@qq.com",
    py_modules=['baizhanchinese.demo1','baizhanchinese.demo2'] #测试要发布的模块
)