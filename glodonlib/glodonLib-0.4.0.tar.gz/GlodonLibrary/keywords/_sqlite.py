# coding:utf-8
import sqlite3

from robot.api import logger


class SqliteDB(object):
    def __init__(self, f_path):
        self.f_path = f_path
    
    def __enter__(self):
        self.conn = sqlite3.connect(self.f_path)
        self.cursor = self.conn.cursor()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            raise Exception(exc_val)
        else:
            self.cursor.close()
            self.conn.close()
    
    def execute(self, sql):
        if sql is None or sql == '':
            raise ValueError('sql 不能为空!')
        if 'delete' in sql.lower() or 'update' in sql.lower() or 'insert' in sql.lower():
            # print sql
            try:
                self.cursor.execute(sql)
            except Exception as e:
                self.conn.rollback()
                logger.error("db 处理失败!")
                raise Exception('处理失败：' + str(e.message))
            else:
                self.conn.commit()
        else:
            # print sql
            try:
                
                self.cursor.execute(sql)
            except Exception as e:
                # logger.info(e,also_console=True)
                raise e
    
    def fetchall(self):
        return self.cursor.fetchall()
    
    def fetchone(self):
        return self.cursor.fetchone()
    
    def fetchmany(self, size):
        return self.cursor.fetchmany(size)


if __name__ == '__main__':
    pass
