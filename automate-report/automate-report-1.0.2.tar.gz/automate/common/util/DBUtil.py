#coding=utf-8
__author__ = 'circlq'

import pymysql.connections as db_connection
import pymysql.cursors


def init(db_host, db_port, user, password, db):
    """
    数据库初始化, 并返回connection 对象

    """
    connection = db_connection.Connection(host=db_host, port=int(db_port),
                                               user=user, password=password,
                                              database=db, charset='utf8', init_command='SET NAMES UTF8')

    return connection


def execute_query_sql(connection, sql):
    """
    执行:sql语句
    :param sql:
    :return: 返回查询的结果, fetchall, 返回的是一个list
    """
    # 获取一个游标对象
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    # 执行sql
    cursor.execute(sql)

    return cursor.fetchall()


def execute_commit_sql(connection, sql):
    # 获取一个游标对象
    """
    执行update操作: 包括:update、delete、insert等操作, 都需要commit
    :param sql:
    """
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # 执行sql
    cursor.execute(sql)

    # if execute: update or delete or insert , must commit
    connection.commit()


def close_connection(connection):
    """
    关闭数据库连接
    """
    connection.close()
