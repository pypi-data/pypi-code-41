# encoding:utf8
''' sqlite3库封装 '''
import os
import sys
import sqlite3
import logging
from functools import wraps


def db_chk_course(method):
    ''' 数据库、游标检查 '''
    @wraps(method)
    def _tarfunc(self, *args, **kwads):
        if self.conn() is None:
            logging.error("Not create the conn yet!")
            return
        if self.course() is None:
            logging.error("Not find the db-course yet!")
            return
        return method(self, *args, **kwads)
    return _tarfunc


class SqliteObj(object):
    ''' 连接实例 '''
    _conn = None                # 链接实例
    _conncour = None            # 游标
    _isdebug = True             # 是否是开发调试

    TBCONF_NAME = dict(         # 表结构默认
        int="int(11)",
        str="varchar(20)"
    )

    DATA_FORAMTFUNC = dict(     # 表内数据格式转换
        int=lambda val: str(int(val)) + ",",
        str=lambda val: "'{val}'".format(val=val)
    )

    DB_COMMANDS = dict(         # 数据库操作文本
        newtb='''CREATE TABLE IF NOT EXISTS {tbname} ({tbchk} PRIMARY KEY('{privatekey}'))''',
        insert='''INSERT INTO {tbname} VALUES ({datachk})''',
        getdata='''SELECT * FROM {tbname} WHERE {condition}''',
        getcount='''SELECT COUNT * FROM {tbname} WHERE {condition}''',
        insertlist='''INSERT INTO {tbname} VALUES {datachk}''',
        update='''UPDATE {tbname} SET {valstr} WHERE {condition}'''
    )

    def __init__(self, dbfile):
        if (os.path.isfile(dbfile)) and (self._isdebug is False):
            logging.error("DB is still exist! Del it first!")
            sys.exit()
        if self._conn is None:
            self._conn = sqlite3.connect(dbfile)
            self._conncour = self._conn.cursor()

    def __del__(self):
        if self._conncour:
            logging.info("Close clourse")
            self._conncour.close()

    def conn(self):
        ''' 库连接 '''
        return self._conn

    def course(self):
        ''' 库游标 '''
        return self._conncour

    def _chk_tbocnf(self, tbconf):
        cmd_str = ""
        for col in tbconf:
            for key, keytype in col.items():
                cmd_str += "'{key}' {keyval} NOT NULL,".format(
                    key=key, keyval=self.TBCONF_NAME[keytype])
        return cmd_str

    def _chk_insert(self, datacont):
        cmd_str = ""
        for valtype, val in datacont.items():
            relvaltype = valtype[:3]
            relindex = int(valtype[-1]) - 1
            cmd_str += self.DATA_FORAMTFUNC[relvaltype](val) + ","
        return cmd_str[:-1]

    def _chk_insertlist(self, datalist):
        ret = ""
        cmd_str = ""
        for dataobj in datalist:
            liststr = "({}),"
            listval = []
            for valtype, val in dataobj.items():
                relvaltype = valtype[:3]
                relindex = int(valtype[-1]) - 1
                listval.insert(
                    relindex, self.DATA_FORAMTFUNC[relvaltype](val) + ",")
            cmd_str += liststr.format("".join(listval)[:-1])
            ret += cmd_str
        return ret[:-1]

    @db_chk_course
    def _excute_cmd(self, cmdstr):
        ''' 执行SQL命令 '''
        logging.debug("insert cmd->>>%s", cmdstr)
        try:
            cu = self._conncour.execute(cmdstr)
            self._conn.commit()
            return cu
        except sqlite3.OperationalError as excuterr:
            logging.error(
                "\n============\nsqlite excute %s error!\n%s\n============\n", cmdstr, excuterr)
            return
        except sqlite3.IntegrityError as interr:
            logging.error(
                "\n============\nsqlite excute %s error!\n%s\n============\n", cmdstr, interr)
            return

    @db_chk_course
    def create_table(self, tbname, tbconf, privatekey=""):
        ''' 创建表 '''
        if privatekey is "":
            keylist = list(tbconf[0].keys())
            privatekey = keylist[0]
        logging.debug("--->>privatekey  %s", privatekey)
        tbchk = self._chk_tbocnf(tbconf)
        cmd_str = self.DB_COMMANDS["newtb"].format(
            tbname=tbname, tbchk=tbchk, privatekey=privatekey)
        self._excute_cmd(cmd_str)

    @db_chk_course
    def get_data(self, tbname, condition):
        ''' 获取数据 '''
        cmd_str = self.DB_COMMANDS["getdata"].format(
            tbname=tbname, condition=condition)
        cu = self._excute_cmd(cmd_str)
        return cu.fetchall()

    @db_chk_course
    def get_keycount(self, tbname, condition):
        ''' 获取字段数量 '''
        cmd_str = self.DB_COMMANDS["getcount"].format(
            tbname=tbname, condition=condition)
        self._excute_cmd(cmd_str)

    @db_chk_course
    def insert_data(self, tbname, dbdata):
        ''' 添加单条数据 '''
        cmd_str = self.DB_COMMANDS["insert"].format(
            tbname=tbname, datachk=self._chk_insert(dbdata))
        self._excute_cmd(cmd_str)

    @db_chk_course
    def insert_datalist(self, tbname, dbdatalist):
        ''' 添加多条数据 '''
        cmd_str = self.DB_COMMANDS["insertlist"].format(
            tbname=tbname, datachk=self._chk_insertlist(dbdatalist))
        self._excute_cmd(cmd_str)

    @db_chk_course
    def update_data(self, tbname, valstr, condition):
        ''' 更新单条数据 '''
        cmd_str = self.DB_COMMANDS["update"].format(
            tbname=tbname, valstr=valstr, condition=condition)
        self._excute_cmd(cmd_str)

    @db_chk_course
    def close(self):
        ''' 关闭连接 '''
        self._conncour.close()


class SqliteMgr(object):
    ''' sqlite单例 '''
    _dbobj = None  # 连接单例

    @classmethod
    def inc(cls, dbfile=""):
        ''' inc '''
        if cls._dbobj is None:
            cls._dbobj = SqliteObj(dbfile)
        return cls._dbobj

    @classmethod
    def close_all(cls):
        ''' 关闭连接 '''
        cls._dbobj.close()
        del cls._dbobj


__all__ = [
    "SqliteMgr"
]

if __name__ == "__main__":

    '''
    usage:
    TBNAME = "RES_MD5"
    TBCONF = dict(
        id="int",
        number="str"
    )

    DATACONT = dict(
        int=1,
        str="1231ada"
    )

    SqliteMgr.inc("C:\\testsqlite.db").create_table(TBNAME, TBCONF, "id")
    SqliteMgr.inc("C:\\testsqlite.db").insert_data(TBNAME, DATACONT)
    SqliteMgr.close_all()

    '''
