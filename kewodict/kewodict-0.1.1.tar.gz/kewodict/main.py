# import pymysql
#
# class Dict:
#     database = "localhost"
#     _whereCondition=''
#
#     # 初始化
#     def __init__(self,host = "localhost",username = "root",password = "",database = "kewo"):
#         self.host = host
#         self.username = username
#         self.password = password
#         self.database = database
#         self.db = None
#         self.cur = None
#         Dict.database = database
#
#
#     # 连接数据库
#     def connectDB(self):
#         try:
#             self.db = pymysql.connect(self.host,self.username,self.password,self.database)
#         except:
#             print("数据库连接出错")
#             return False;
#         self.cur = self.db.cursor()
#
#         return True;
#
#     # 关闭数据库
#     def closeDB(self):
#         if self.db and self.cur:
#             self.cur.close()
#             self.db.close()
#
#     # 执行数据库语句
#     def excute(self,sql,params=None,commit=False):
#         # 连接数据库
#         conn = self.connectDB()
#         if not conn:
#             return False;
#         try:
#             if self.db and self.cur:
#                 rowcount = self.cur.execute(sql,params)
#                 if commit:
#                     self.db.commit()
#                 else:
#                     pass
#                 return rowcount
#
#         except:
#             self.closeDB()
#             return False
#
#
#     # 查询多条数据
#     def fetchAll(self,sql,params=None):
#         sql = "select * from `admin_users`"
#         res = self.excute(sql,params)
#         if not res:
#             return False
#         self.closeDB()
#         res = self.cur.fetchall()
#
#         return res
#
#     # 设定条件
#     def where(self,num) :
#         print(num)
#         self._whereCondition += num
#         print(self._whereCondition)
#         return self
#
#     # 执行
#     def __get(self):
#         print("333")
#
#     def aa(self):
#         print("123")
#     def bb(self):
#         print("234")
