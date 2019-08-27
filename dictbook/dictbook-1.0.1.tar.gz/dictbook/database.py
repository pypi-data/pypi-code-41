import sqlite3 
import os

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

    def insert(self, word, meaning, date):
        insert = 'insert into {} values (?, ?, ?)'.format(self.tb_name)
        with sqlite3.connect(self.db_name) as conn:
            conn.execute(insert, (word, meaning, date))

    def content(self):    
        return 

if __name__ == '__main__':
    db = Database('test.db', 'words')
    db.content()