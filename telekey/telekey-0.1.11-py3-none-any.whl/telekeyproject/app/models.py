import peewee

db = peewee.SqliteDatabase('app.db')
db.connect()


if __name__ == "__main__":
    db.create_tables([])
