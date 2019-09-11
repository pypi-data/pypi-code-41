import MySQLdb
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL


class ConnectionHandler(object):
    """
    This class can be used for database connection.
    """

    def __init__(self, username, password, ip, port="3306"):
        self.__username = username
        self.__password = password
        self.__ip = ip
        self.__port = port

        self.con_url1 = {"drivername": "mysql+mysqldb",
                         "username": self.__username,
                         "password": self.__password,
                         "host": self.__ip,
                         "port": str(self.__port)}

        self.con_url2 = {"user": self.__username,
                         "password": self.__password,
                         "host": self.__ip,
                         "port": int(self.__port)}

        self.con_engine = create_engine(URL(**self.con_url1))

    def execute(self, sql, mysql_db=False, get_data=True):
        """
        It executes the any type of sql query.
        """
        try:
            if mysql_db:
                conn = MySQLdb.connect(**self.con_url2)
                cur = conn.cursor()
                cur.execute(sql)
                if get_data:
                    cols = [cur.description[i][0] for i in
                            range(len(cur.description))]
                    df = pd.DataFrame(list(cur.fetchall()), columns=cols)

                    return df
            else:
                return pd.read_sql(sql=query, con=self.con_engine)

        except Exception as e:
            raise Exception(e)

        finally:
            try:
                conn.close()
            except Exception:
                pass

if __name__ == "__main__":
    ch = ConnectionHandler("sagar", "3Xtenso@123", "localhost")
    query = """SELECT account_number, customer_code from MASTER_DATA.md_accounts limit 10"""
    df = ch.execute(sql=query, mysql_db=True)
    df.head()
