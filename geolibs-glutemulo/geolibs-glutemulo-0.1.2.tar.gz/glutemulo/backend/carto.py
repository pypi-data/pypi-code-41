import operator
import time

from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.sql import CopySQLClient, SQLClient

from glutemulo.backend.sql import SQLBackend
from glutemulo.config import config
from glutemulo.logger import log


def _get_auth_client():
    log.debug(f"Using {config['carto_api_url']}")
    auth_client = APIKeyAuthClient(
        api_key=config["carto_api_key"], base_url=config["carto_api_url"]
    )
    return auth_client


def query(sql_query, parse_json=True, do_post=True, format=None, retries=5):
    log.debug(f"Query: {sql_query}")
    sql = SQLClient(_get_auth_client(), api_version="v2")
    res = None

    for retry_number in range(retries):
        try:
            res = sql.send(sql_query, parse_json, do_post, format)

            if res:
                break

        except CartoException as carto_exception:
            if retry_number == retries - 1:
                raise carto_exception
            else:
                time.sleep(5)
                continue

    if format is None:
        return res["rows"]

    return res


def copy(tablename, rows, delimiter=",", quote='"', headers=None):
    copy_client = CopySQLClient(_get_auth_client())
    rows = iter(rows)
    if headers is None:
        headers = delimiter.join(next(rows))
    else:
        headers = delimiter.join(headers)

    from_query = f"""COPY {tablename} ({headers}) FROM stdin
        (FORMAT CSV, DELIMITER '{delimiter}', HEADER false)"""
    try:
        return copy_client.copyfrom(from_query, rows_generator(rows, delimiter, quote))
    except CartoException as e:
        log.error(f"Error importing \n\n {rows}")
        log.exception(e)


def rows_generator(rows, delimiter, quote):
    # note the \n to delimit rows
    for r in rows:
        yield bytearray(
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
            + "\n",
            "utf-8",
        )


def create_table_if_not_exists(
    tablename, table_definition, table_indexes="", cartodbfy=True
):
    tables = map(
        operator.itemgetter("cdb_usertables"), query("SELECT CDB_UserTables()")
    )
    if tablename in tables:
        return
    log.info(f'Creating not found table "{tablename}"')
    query(f"CREATE TABLE IF NOT EXISTS {tablename} ({table_definition})")
    log.debug("Adding indexes")
    for idx in table_indexes.splitlines():
        if not idx:
            continue
        log.debug(f"{idx}")
        query(idx)
    if cartodbfy:
        log.debug("Cartodbfing table")
        query(f"SELECT CDB_CartodbfyTable(current_schema, '{tablename}')")


class CartoBackend(SQLBackend):
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
