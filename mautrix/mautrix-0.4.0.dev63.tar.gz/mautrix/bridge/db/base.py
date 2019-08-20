# Copyright (c) 2019 Tulir Asokan
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from typing import Iterator, Optional, Generic, TypeVar, Type, Dict, List, Any

from sqlalchemy import Table, Constraint
from sqlalchemy.engine.base import Engine, Connection
from sqlalchemy.engine.result import RowProxy, ResultProxy
from sqlalchemy.sql.base import ImmutableColumnCollection
from sqlalchemy.sql.expression import Select, ClauseElement, and_
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.dialects.postgresql import insert as pg_insert

T = TypeVar('T', bound='Base')


@as_declarative()
class Base:
    """
    Base class for SQLAlchemy models. Provides SQLAlchemy declarative base features and some
    additional utilities.
    """

    db: Engine
    t: Table
    __table__: Table
    c: ImmutableColumnCollection
    column_names: List[str]

    @classmethod
    def _one_or_none(cls: Type[T], rows: ResultProxy) -> Optional[T]:
        """
        Try scanning one row from a ResultProxy and return ``None`` if it fails.

        Args:
            rows: The SQLAlchemy result to scan.

        Returns:
            The scanned object, or ``None`` if there were no rows.
        """
        try:
            return cls.scan(next(rows))
        except StopIteration:
            return None

    @classmethod
    def _all(cls: Type[T], rows: ResultProxy) -> Iterator[T]:
        """
        Scan all rows from a ResultProxy.

        Args:
            rows: The SQLAlchemy result to scan.

        Yields:
            Each row scanned with :meth:`scan`
        """
        for row in rows:
            yield cls.scan(row)

    @classmethod
    def scan(cls: Type[T], row: RowProxy) -> T:
        """
        Read the data from a row into an object.

        Args:
            row: The RowProxy object.

        Returns:
            An object containing the information in the row.
        """
        return cls(**dict(zip(cls.column_names, row)))

    @classmethod
    def _make_simple_select(cls: Type[T], *args: ClauseElement) -> Select:
        """
        Create a simple ``SELECT * FROM table WHERE <args>`` statement.

        Args:
            *args: The WHERE clauses. If there are many elements, they're joined with AND.

        Returns:
            The SQLAlchemy SELECT statement object.
        """
        if len(args) > 1:
            return cls.t.select().where(and_(*args))
        elif len(args) == 1:
            return cls.t.select().where(args[0])
        else:
            return cls.t.select()

    @classmethod
    def _select_all(cls: Type[T], *args: ClauseElement) -> Iterator[T]:
        """
        Select all rows with given conditions. This is intended to be used by table-specific
        select methods.

        Args:
            *args: The WHERE clauses. If there are many elements, they're joined with AND.

        Yields:
            The objects representing the rows read with :meth:`scan`
        """
        yield from cls._all(cls.db.execute(cls._make_simple_select(*args)))

    @classmethod
    def _select_one_or_none(cls: Type[T], *args: ClauseElement) -> T:
        """
        Select one row with given conditions. If no row is found, return ``None``. This is intended
        to be used by table-specific select methods.

        Args:
            *args: The WHERE clauses. If there are many elements, they're joined with AND.

        Returns:
            The object representing the matched row read with :meth:`scan`, or ``None`` if no rows
            matched.
        """
        return cls._one_or_none(cls.db.execute(cls._make_simple_select(*args)))

    def _constraint_to_clause(self, constraint: Constraint) -> ClauseElement:
        return and_(*[column == self.__dict__[name]
                      for name, column in constraint.columns.items()])

    @property
    def _edit_identity(self: T) -> ClauseElement:
        """The SQLAlchemy WHERE clause used for editing and deleting individual rows.
        Usually AND of primary keys."""
        return self._constraint_to_clause(self.t.primary_key)

    def edit(self: T, *, _update_values: bool = True, **values) -> None:
        """
        Edit this row.

        Args:
            _update_values: Whether or not the values in memory should be updated as well as the
                            values in the database.
            **values: The values to change.
        """
        with self.db.begin() as conn:
            conn.execute(self.t.update()
                         .where(self._edit_identity)
                         .values(**values))
        if _update_values:
            for key, value in values.items():
                setattr(self, key, value)

    def delete(self: T) -> None:
        """Delete this row."""
        with self.db.begin() as conn:
            conn.execute(self.t.delete().where(self._edit_identity))

    @property
    def _insert_values(self: T) -> Dict[str, Any]:
        """Values for inserts. Generally you want all the values in the table."""
        return {column_name: self.__dict__[column_name]
                for column_name in self.column_names}

    def insert(self) -> None:
        with self.db.begin() as conn:
            conn.execute(self.t.insert().values(**self._insert_values))

    @property
    def _upsert_values(self: T) -> Dict[str, Any]:
        """The values to set when an upsert-insert conflicts and moves to the update part."""
        return self._insert_values

    def _upsert_postgres(self: T, conn: Connection) -> None:
        conn.execute(pg_insert(self.t).values(**self._insert_values)
                     .on_conflict_do_update(constraint=self.t.primary_key,
                                            set_=self._upsert_values))

    def _upsert_sqlite(self: T, conn: Connection) -> None:
        conn.execute(self.t.insert().values(**self._insert_values).prefix_with("OR REPLACE"))

    def _upsert_generic(self: T, conn: Connection):
        conn.execute(self.t.delete().where(self._edit_identity))
        conn.execute(self.t.insert().values(**self._insert_values))

    def upsert(self: T) -> None:
        with self.db.begin() as conn:
            if self.db.dialect.name == "postgresql":
                self._upsert_postgres(conn)
            elif self.db.dialect.name == "sqlite":
                self._upsert_sqlite(conn)
            else:
                self._upsert_generic(conn)

    def __iter__(self):
        for key in self.column_names:
            yield self.__dict__[key]
