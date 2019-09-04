from . import countyCSV, roadStreetCSV, villageCSV, DEBUG_PRINT
import csv
import sqlite3

def createDB():
    conn = sqlite3.connect('test.db')
    print('Opened database successfully')

    def existTable(tableName):
        c = conn.cursor()
        c.execute(''' SELECT count(name) FROM sqlite_master
                    WHERE type='table' AND name='{}' '''.format(tableName))

        if c.fetchone()[0] != 0:
            conn.execute('DROP TABLE {}'.format(tableName))
            print(f'{tableName} Table drop successfully')

    existTable('COUNTY')
    existTable('ROADSTREET')
    existTable('VILLAGE')
    conn.commit()

    # COUNTY
    conn.execute('''CREATE TABLE COUNTY
                    (ZIPCODE CHAR(10) NOT NULL,
                    COUNTY CHAR(20) NOT NULL,
                    ENCOUNTY TEXT NOT NULL);''')
    print('COUNTY Table created successfully')

    csvfile = open(countyCSV, 'r')
    rows = csv.reader(csvfile)

    for row in rows:
        conn.execute('insert into COUNTY values (?, ?, ?);', (
                    row[0],
                    row[1],
                    row[2]))
    conn.commit()

    # ROADSTREET
    conn.execute('''CREATE TABLE ROADSTREET
                    (ROADSTREET CHAR(30) NOT NULL,
                    ENROADSTREET TEXT NOT NULL);''')
    print('ROADSTREET Table created successfully')

    csvfile = open(roadStreetCSV, 'r')
    rows = csv.reader(csvfile)

    for row in rows:
        conn.execute('insert into ROADSTREET values (?, ?);', (
                    row[0],
                    row[1]))
    conn.commit()

    # VILLAGE
    conn.execute('''CREATE TABLE VILLAGE
                    (VILLAGE CHAR(30) NOT NULL,
                    ENVILLAGE TEXT NOT NULL);''')
    print('VILLAGE Table created successfully')

    csvfile = open(villageCSV, 'r')
    rows = csv.reader(csvfile)

    for row in rows:
        conn.execute('insert into VILLAGE values (?, ?);', (
                    row[0],
                    row[1]))
    conn.commit()
    if not DEBUG_PRINT:
        for row in conn.execute("SELECT * FROM COUNTY LIMIT 10"):
            print(row)

        for row in conn.execute("SELECT * FROM ROADSTREET LIMIT 10"):
            print(row)

        for row in conn.execute("SELECT * FROM VILLAGE LIMIT 100"):
            print(row)

    conn.close()




def selectCounty(county):
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute("SELECT * FROM COUNTY WHERE COUNTY=?", (county,))

    rows = c.fetchall()
    if len(rows) ==1:
        return rows
    for row in rows:
        print(row)



if __name__ == '__main__':
    createDB()


