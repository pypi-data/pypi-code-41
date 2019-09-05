from abc import ABC, abstractmethod
from typing import Dict, Any
from psycopg2 import connect
from .versioner import Versioner


class SqlVersioner(Versioner):
    def __init__(self, context: Dict[str, Any]) -> None:
        self.schema = context.get('schema', '__template__')
        self.connection = context['connection']
        self.table = '__version__'
        self._setup()

    @property
    def version(self) -> str:
        with self.connection.cursor() as cursor:
            query = (f"SELECT version FROM {self.schema}.{self.table} "
                     "ORDER BY created_at DESC LIMIT 1")
            cursor.execute(query)
            result = cursor.fetchone()
            version = result and next(iter(result)) or ''

        return version

    @version.setter
    def version(self, value: str) -> None:
        with self.connection.cursor() as cursor:
            query = (f"INSERT INTO {self.schema}.{self.table} (version) "
                     "VALUES (%s);")
            parameters = (value,)
            cursor.execute(query, parameters)

    def _setup(self) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(
                f'CREATE SCHEMA IF NOT EXISTS {self.schema}')
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {self.schema}.{self.table}("
                "id serial PRIMARY KEY, "
                "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
                "version VARCHAR(255) NOT NULL)")
