import sqlite3
import pkg_resources

DB_FILE = "data/zeitzono.sqlite"

MAX_LIMIT_AMT = 100


class ZeitzonoDB:
    def __init__(self):

        dbfile = pkg_resources.resource_filename("Zeitzono", DB_FILE)
        self.conn = sqlite3.connect(dbfile)

    def _sql_gen(
        self,
        term1,
        term2=None,
        subterm=None,
        count=False,
        limit=False,
        limitamt=25,
    ):

        select_line = """select cities.asciiname, countries.name,
                                admin1.name, admin2.name, cities.timezone"""

        if count:
            select_line = "select count(asciiname)"

        from_line = "from cities"

        on_line = """left join countries on (cities.countrycode = countries.countrycode)
                     left join admin1 on (admin1.code = (cities.countrycode || '.' || cities.admin1))
                     left join admin2 on (admin2.code = (cities.countrycode || '.' || cities.admin1 || '.' || cities.admin2))
                  """  # noqa

        if term2 is None and subterm is None:
            where_line = """
                         where cities.alternatenames like ?
                         OR
                         cities.name like ?
                         OR
                         cities.asciiname like ?
            """

        if term2 is not None and subterm is None:
            where_line = """where
                            (cities.alternatenames like ?
                            OR
                            cities.name like ?
                            OR
                            cities.asciiname like ?)
                            AND
                            (cities.alternatenames like ?
                            OR
                            cities.name like ?
                            OR
                            cities.asciiname like ?)
                        """

        if term2 is None and subterm is not None:
            where_line = """
                         where (cities.alternatenames like ?
                         OR
                         cities.name like ?
                         OR
                         cities.asciiname like ?)
                         AND
                         (countries.name like ?
                         OR
                         admin1.name like ?
                         OR
                         admin2.name like ?)
                         """

        if term2 is not None and subterm is not None:
            where_line = """where
                            (cities.alternatenames like ?
                            OR
                            cities.name like ?
                            OR
                            cities.asciiname like ?)
                            AND
                            (cities.alternatenames like ?
                            OR
                            cities.name like ?
                            OR
                            cities.asciiname like ?)
                            AND
                            (countries.name like ?
                            OR
                            admin1.name like ?
                            OR
                            admin2.name like ?)
                         """

        order_line = "order by population desc"
        if count:
            order_line = ""

        limit_line = ""
        if limit:
            if limitamt > MAX_LIMIT_AMT:
                limitamt = MAX_LIMIT_AMT
            limit_line = "limit %s" % limitamt

        sql = "\n".join(
            [
                select_line,
                from_line,
                on_line,
                where_line,
                order_line,
                limit_line,
            ]
        )

        return sql

    def db_count(self, term1, term2=None, subterm=None):
        return self.db_search(term1, term2, subterm, count=True)

    def db_search(
        self,
        term1,
        term2=None,
        subterm=None,
        count=False,
        limit=False,
        limitamt=25,
    ):
        sql = self._sql_gen(term1, term2, subterm, count, limit)
        # print(sql, file=open("foo", "a"))
        cursor = self.conn.cursor()

        if term2 is None and subterm is None:
            results = cursor.execute(
                sql, ("%" + term1 + "%", "%" + term1 + "%", "%" + term1 + "%")
            )
        elif term2 is not None and subterm is None:
            results = cursor.execute(
                sql,
                (
                    "%" + term1 + "%",
                    "%" + term1 + "%",
                    "%" + term1 + "%",
                    "%" + term2 + "%",
                    "%" + term2 + "%",
                    "%" + term2 + "%",
                ),
            )
        elif term2 is None and subterm is not None:
            results = cursor.execute(
                sql,
                (
                    "%" + term1 + "%",
                    "%" + term1 + "%",
                    "%" + term1 + "%",
                    "%" + subterm + "%",
                    "%" + subterm + "%",
                    "%" + subterm + "%",
                ),
            )
        elif term2 is not None and subterm is not None:
            results = cursor.execute(
                sql,
                (
                    "%" + term1 + "%",
                    "%" + term1 + "%",
                    "%" + term1 + "%",
                    "%" + term2 + "%",
                    "%" + term2 + "%",
                    "%" + term2 + "%",
                    "%" + subterm + "%",
                    "%" + subterm + "%",
                    "%" + subterm + "%",
                ),
            )

        if count:
            return cursor.fetchone()[0]

        return reversed(results.fetchall())

    def random_cities(self, count):
        rsql = """
                      select cities.asciiname, countries.name, admin1.name, admin2.name, cities.timezone
                      from cities
                      left join countries on (cities.countrycode = countries.countrycode)
                      left join admin1 on (admin1.code = (cities.countrycode || '.' || cities.admin1))
                      left join admin2 on (admin2.code = (cities.countrycode || '.' || cities.admin1 || '.' || cities.admin2))
                      where cities.rowid in (select rowid from cities order by random() limit %s)"""  # noqa
        rsql = rsql % count
        cursor = self.conn.cursor()
        results = cursor.execute(rsql)
        return results.fetchall()
