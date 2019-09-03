# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    TEXT
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime
import json
import os

Base = declarative_base()
print(os.path.join(os.getcwd(), 'dbs', 'rule.db'))
engine = create_engine('sqlite:///{}?check_same_thread=False'.format(os.path.join(os.getcwd(), 'dbs', 'rule.db')), echo=False)
Session = sessionmaker(bind=engine)
session = Session()


class DB_Operation(Base):
    '''数据库操作记录类'''
    __tablename__ = 't_operation'

    db_version_id = Column(Integer,primary_key=True)
    db_method = Column(String(10), nullable=True, comment='方法名称 添加a  删除r  更新u')  # 方法名称 添加a  删除r  更新u
    db_table = Column(String(50), nullable=True, comment='数据库中表的名称')  # 数据库中表的名称
    db_table_id = Column(Integer, comment='数据表的id')  # 数据表的id
    db_content = Column(TEXT, nullable=True, comment='数据操作的内容')  # 数据操作的内容
    db_des = Column(String(100), nullable=True, comment='')  #


class Rule_Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    category_name = Column(String(100), nullable=True)  # 类别名称
    category_des = Column(String(100), )  # 类别描述
    category_def = Column(String(100), )  # 未定义
    category_create_time = Column(DateTime, default=datetime.datetime.now)  # 创建分类的时间

    rules = relationship('Rule', backref='category', lazy=True)


class Rule(Base):
    '''
    规则库
    '''
    __tablename__ = 'rule'
    id = Column(Integer, primary_key=True)
    rule_name = Column(String(100), nullable=True) # 规则名称
    rule_version = Column(String(100), ) # 规则版本
    rule_tag = Column(Integer, ForeignKey('category.id')  ) # 规则标签 外键Rule_Category
    rule_method = Column(String(100), ) # 识别方式[header.主页,404,url,urlmd5,status]
    rule_pattern =Column(TEXT, nullable=True)  # 规则内容   看下之后这里的内容能不能用json表示
    rule_join_url = Column(String(100), ) # 拼接的url内容


    demo_url = Column(String(100), ) # 示例域名
    rule_founder = Column(String(100), ) # 创建这条规则的人 未定义
    rule_des = Column(String(100), default=None) # 规则的描述
    rule_undefined = Column(String(100), ) # 内容未定义

    rule_create_time = Column(String(100),) # 创建规则的时间
    rule_update_time = Column(String(100),) # 更新规则的时间
    rule_status = Column(String(100), nullable=False ,default='forbid',comment='规则的状态 默认 禁用 forbid 为0 测试为test 1 公开 public 2  私有private 3') # 规则的状态 默认active 1 禁用 为0


class Rule_Version(Base):
    '''
    规则库版本
    '''
    __tablename__ = 'r_version'
    version_id = Column(Integer, primary_key=True)
    rule_name = Column(String(100), nullable=True)  # 规则名称
    rule_version = Column(String(100), )  # 规则版本
    rule_tag = Column(Integer, ForeignKey('category.id'))  # 规则标签 外键Rule_Category
    rule_method = Column(String(100), )  # 识别方式[header.主页,404,url,urlmd5,status]
    rule_pattern = Column(TEXT, nullable=True)  # 规则内容   看下之后这里的内容能不能用json表示
    rule_join_url = Column(String(100), )  # 拼接的url内容

    demo_url = Column(String(100), )  # 示例域名
    rule_founder = Column(String(100), )  # 创建这条规则的人 未定义
    rule_des = Column(String(100), )  # 规则的描述
    rule_undefined = Column(String(100), )  # 内容未定义

    rule_create_time = Column(String(100),)  # 创建规则的时间
    rule_update_time = Column(String(100),)  # 更新规则的时间
    rule_status = Column(String(100), nullable=False, default='forbid',
                         comment='规则的状态 默认 禁用 forbid 为0 测试为test 1 公开 public 2  私有private 3')  # 规则的状态 默认active 1 禁用 为0

def init_db():

    # 判断是否存在数据库
    if not os.path.exists(os.path.join(os.getcwd(), 'dbs', 'rule.db')):
        if not os.path.exists(os.path.join(os.getcwd(), 'dbs')):
            os.mkdir(os.path.join(os.getcwd(), 'dbs'))
        Base.metadata.create_all(engine)  # 找到所有继承了Base的类，按照其结构建表
    # else: # 测试的数据.线上环境不需要
    #     Base.metadata.drop_all(engine) # 删除数据
    #     Base.metadata.create_all(engine)  # 找到所有继承了Base的类，按照其结构建表



if __name__ == '__main__':
    print('***************初始化数据库*****************')
    init_db()
    print("***************同步数据****************")

