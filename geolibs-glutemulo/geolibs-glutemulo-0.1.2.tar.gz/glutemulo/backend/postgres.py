import io

import psycopg2
import psycopg2.extras

from glutemulo.backend.sql import SQLBackend
from glutemulo.config import config
from glutemulo.logger import log

_conn = None


def get_connection():
    global _conn
    if _conn is not None:
        return _conn
    _conn = psycopg2.connect(
        config["postgres_uri"], cursor_factory=psycopg2.extras.NamedTupleCursor
    )
    _conn.autocommit = True
    return _conn


def copy(tablename, rows, delimiter=",", quote='"', headers=None):
    rows = iter(rows)
    if headers is None:
        headers = delimiter.join(next(rows))
    else:
        headers = delimiter.join(headers)

    from_query = f"""COPY {tablename} ({headers}) FROM stdin
        (FORMAT CSV, DELIMITER '{delimiter}', HEADER false)"""
    with get_connection().cursor() as cur:
        try:
            return cur.copy_expert(from_query, _rows_as_file(rows, delimiter, quote))
        except psycopg2.Error as e:
            log.error(f"Error importing \n\n {rows}")
            log.exception(e)


def _rows_as_file(rows, delimiter, quote):
    return io.StringIO(
        "\n".join(
            delimiter.join(
                [
                    "{}{}{}".format(
                        quote, str(e).replace(f"{quote}", f"{quote}{quote}"), quote
                    )
                    if e
                    else ""
                    for e in r
                ]
            )
            for r in rows
        )
    )


def create_table_if_not_exists(tablename, table_definition, table_indexes=""):
    with get_connection().cursor() as cur:
        cur.execute("SELECT * FROM pg_catalog.pg_tables")
        for table in cur.fetchall():
            if tablename == table.tablename:
                return
        log.info(f'Creating not found table "{tablename}"')
        cur.execute(f"CREATE TABLE IF NOT EXISTS {tablename} ({table_definition})")
        log.debug("Adding indexes")
        for idx in table_indexes.splitlines():
            if not idx:
                continue
            log.debug(f"{idx}")
            cur.execute(idx)


class PostgresBackend(SQLBackend):
    def copy(self, rows, delimiter=",", quote='"'):
        return copy(
            self.table_name,
            rows,
            delimiter=delimiter,
            quote=quote,
            headers=self.columns,
        )

    def create_table_if_not_exists(self, tablename, table_definition, table_indexes=""):
        return create_table_if_not_exists(tablename, table_definition, table_indexes)
