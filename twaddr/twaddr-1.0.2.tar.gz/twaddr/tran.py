# translation
import sqlite3

addr = '41349 臺中市霧峰區吉峰東路168號'
county = '臺中市霧峰區'
village = '南富村'
roadStreet = '吉峰東路'




def selectCounty(county):
    conn = sqlite3.connect('test.db')
    # c = conn.cursor()
    # c.execute("SELECT * FROM COUNTY WHERE COUNTY=?", (county,))

    c = conn.cursor()
    c.execute('SELECT * FROM COUNTY WHERE COUNTY LIKE \"%{0}%\"'.format(county,))

    rows = c.fetchall()
    if len(rows) == 1:
        return rows[0][2]
    if len(rows) == 0:
        return '搜尋無果'
    return rows
    return '搜尋數目大於 1'


enAddr = selectCounty(county)
print(enAddr)
#==============================================================
# 縣市
# 鄉鎮市區
# 道路 街名 村里名稱
#
# 檔案
# 縣市鄉鎮
# 村里文字巷
# 路街ㄎ
#==============================================================