# coding:utf-8

import pymysql


class Mysqldb(object):
    """
    mysql数据库的连接操作，示例在下方。
    """

    def __init__(self, host, user, passwd, dbase, port=3306, charset='utf8'):
        self.host, self.user, self.passwd, self.dbase, self.port, self.charset = host, user, passwd, dbase, port, charset
    
    def get_self(self):
        self.conn = pymysql.connect(host=self.host,
                                    user=self.user,
                                    password=self.passwd,
                                    database=self.dbase,
                                    port=self.port,
                                    charset=self.charset
                                    )
        self.cursor = self.conn.cursor()
        return self
    
    def __enter__(self):
        self.conn = pymysql.connect(host=self.host,
                                    user=self.user,
                                    password=self.passwd,
                                    database=self.dbase,
                                    port=self.port,
                                    charset=self.charset
                                    )
        self.cursor = self.conn.cursor()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            self.cursor.close()
            self.conn.close()
        else:
            print(exc_val)
    
    def execute(self, sql):
        if sql is None or sql == '':
            raise ValueError('sql 不能为空!')
        if bool('delete' in sql.lower()) or bool('update' in sql.lower()) or bool('insert' in sql.lower()):
            try:
                self.cursor.execute(sql)
            except Exception as e:
                self.conn.rollback()
                raise e
            else:
                self.conn.commit()
                # logger.info(u'db事务处理成功', also_console=True)
        else:
            try:
                self.cursor.execute(sql)
            except Exception as e:
                raise e
    
    def fetchall(self):
        return self.cursor.fetchall()
    
    def fetchone(self):
        return self.cursor.fetchone()
    
    def fetchmany(self, size):
        return self.cursor.fetchmany(size)


if __name__ == '__main__':
    pass

