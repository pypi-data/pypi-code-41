from sql_tools import sqlite

sqlite.connect("sample.db")
sqlite.execute("CREATE TABLE TEST1 (C1 TEXT);")
sqlite.execute("CREATE TABLE TEST2 (C2 TEXT);")
sqlite.execute("CREATE TABLE TEST3 (C3 TEXT);")
sqlite.execute("CREATE TABLE TEST4 (C4 TEXT);")
