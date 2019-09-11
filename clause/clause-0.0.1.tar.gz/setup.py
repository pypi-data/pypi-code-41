# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
LONGDOC = """
Clause Python SDK
===

Clause项目QQ交流群：809987971

Clause
---

Chatopera Language Understanding Service，Chatopera 语义理解服务

Clause 是帮助中小型企业快速而低成本的获得好用的语义理解服务的系统。

Clause 是 Chatopera 团队自主研发及使用其他商业友好的开源软件的方式实现的，Clause 为实现企业聊天机器人提供强大的大脑，包括客服、智能问答和自动流程服务。Clause 利用深度学习，自然语言处理和搜索引擎技术，让机器更加理解人。

https://github.com/chatopera/clause

"""

setup(
    name='clause',
    version='0.0.1',
    description='中文语义理解服务 Python SDK',
    long_description_content_type="text/markdown",
    long_description=LONGDOC,
    author='Hai Liang Wang',
    author_email='hain@chatopera.com',
    url='https://github.com/chatopera/py-clause',
    license="Apache Software License",
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Chinese (Traditional)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Indexing',
        'Topic :: Text Processing :: Linguistic'],
    keywords='chatbot,machine-learning,NLU,NLP',
    packages=find_packages(),
    install_requires=[
        "absl-py>=0.8",
        "thrift==0.11.0"
    ],
    package_data={
        'clause': [
            '**/*.gz',
            '**/*.txt',
            '**/*.vector',
            'LICENSE']})
