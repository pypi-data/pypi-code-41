# from sql_tools import tools
from sql_tools import sqlite
from sql_tools.sqlite import command, pretty

sqlite.connect("ok.db")
print(sqlite.Database().path())
sqlite.execute("CREATE TABLE IF NOT EXISTS STUDENT (NAME TEXT, AGE INT)")

# command.start()

# tools.jsonToSqlite("ok.json", "ok.db", warning=False)

pretty.format_sql("SHOW TABLES;")
