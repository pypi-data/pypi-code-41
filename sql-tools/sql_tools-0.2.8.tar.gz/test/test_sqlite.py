from sql_tools import sqlite
from sql_tools.sqlite import constants
# from sql_tools import pretty

# sqlite.connect(["test/ok.sqlite"], validateDatabase=False)
sqlite.connect(["test/ok.sqlite", "test/ok.sqlite", "test/ok.sqlite"], validateDatabase=False)

# sqlite.execute("CREATE TABLE IF NOT EXISTS STUDENT(NAME TEXT);", commit=False)
# sqlite.execute("INSERT INTO STUDENT VALUES('YOGESH')", logConsole=True)
# sqlite.execute("INSERT INTO STUDENT VALUES('SANDESH')")


# print(sqlite.execute("SELECT * FROM STUDENT", logConsole=True, splitExec=False))
result = sqlite.execute(["SELECT * FROM STUDENT", "SELECT * FROM STUDENT", "SELECT * FROM STUDENT"])
print(result)

# print(sqlite.getNoOfRecords("student"))
# print(sqlite.execTime())
# print(sqlite.Database())
# print(sqlite.processId())

# print(sqlite.io.tableToCSV("STUDENT", index=False))

# print(sqlite.isConnected("test/ok.sqlite"))
