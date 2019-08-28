import pymysql

import datetime
def findAll():
    connection = pymysql.connect(host='localhost',
                                 port=3306,
                                 user='root',
                                 password='root1234',
                                 db='sa_item',
                                 charset='utf8')


    cursor = connection.cursor()
    sql = 'SELECT * FROM `item_demo`'
    cursor.execute(sql)
    # 执行查询 SQL

    results = cursor.fetchall()
    for row in results:
      idd = row[0]
      user_id = row[1]
      action = row[2]
      time = row[3]
      item_id = row[4]
      item_name = row[5]
      # 打印结果
      # print "id=%s,user_id=%s,action=%d,time=%s,item_id=%d,item_name=%d" % \
      #        (idd, user_id, action, time, item_id,item_name )
      print(idd)
      print(user_id)
      print(action)
      print(time)
      print(item_id)
      print(item_name)
    connection.close()


# class item_demo(ob){
#     var id;
#
#
#
#
# }

def insert():
    time =  print(datetime.datetime.now().strftime("%Y.%m.%d-%H:%M:%S"))

    sql = "INSERT INTO item_demo (action,item_time,item_id,item_name,item_bool,item_number,item_str) VALUES" \
          " ('action02','2019-07-24 10:24:19','02','item_name02','2','2','item_str02')"
    connection = pymysql.connect(host='localhost',
                                 port=3306,
                                 user='root',
                                 password='root1234',
                                 db='sa_item',
                                 charset='utf8')

    cursor = connection.cursor()


    cursor.execute(sql)
    connection.commit()

    # return


if __name__ == '__main__':
    insert()
    findAll()