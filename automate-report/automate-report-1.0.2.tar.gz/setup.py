#!/usr/bin/env python

from distutils.core import setup

# 第三方依赖
requires = [
    "unittest2","requests","pymysql"
]

setup(name='automate-report',
      version='1.0.2',
      description='automate-report 是一个编写测试用例后，运行会通过断言结果自动生成报告'
                  '自带http请求跟数据库连接，具体可在下面url前往查看',
      author='circlq',
      author_email='circlq@qq.com',
      url='https://www.jianshu.com/p/2b7711fce7c9',
      packages=['automate.common', 'automate.common.util','automate.runner'],
      install_requires=requires,  # 第三方库依赖
      )
