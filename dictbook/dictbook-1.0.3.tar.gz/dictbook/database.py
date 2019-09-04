import sqlite3
import os
import datetime

class Database:

    def __init__(self, db_name, tb_name):
        self.db_name = db_name
        self.tb_name = tb_name

        schema = '''
        create table {} (
            word                text primary key not null,
            meaning_ch          text,
            time                date
        );
        '''.format(self.tb_name)

        if not os.path.exists(self.db_name):
            with sqlite3.connect(self.db_name) as conn:
                conn.executescript(schema)
        pass

    def insert(self, word, date):
        eng = word.eng
        meaning_ch = str(word.meaning)
        insert = 'insert into {} values (?, ?, ?)'.format(self.tb_name)
        with sqlite3.connect(self.db_name) as conn:
            conn.execute(insert, (eng, meaning_ch, date))

    def content(self, content_name='*', column='time', s='2019-09-01'):
        '''default select content by 'time', can be altered by 'word' '''
        try:
            sql = "select {} from {} where {} = '{}' ".format(content_name, self.tb_name, column, s)
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                for row in cursor.fetchall():
                    print(row)
        except:
            print('no such element in local database.')


if __name__ == '__main__':
    db = Database('./d.db', 'words')
    db.content()
