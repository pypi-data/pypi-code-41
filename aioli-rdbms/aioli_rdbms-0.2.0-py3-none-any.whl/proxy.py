from enum import Enum

import orm

from sqlalchemy import select, func, desc, asc, text, sql

from aioli.exceptions import AioliException, NoMatchFound

from .manager import DatabaseManager


class FilterOperator(Enum):
    EXACT = "__eq__"
    IEXACT = "ilike"
    CONTAINS = "like"
    ICONTAINS = "ilike"
    IN = "in_"
    GT = "__gt__"
    GTE = "__ge__"
    LT = "__lt__"
    LTE = "__le__"


class ModelProxy:
    manager = DatabaseManager

    def __init__(self, model):
        self.model = model

    @property
    def related(self):
        return list(self.model.__related__.keys())

    def _model_has_attrs(self, *attrs):
        for attr in attrs:
            if attr not in self.model.fields:
                raise AioliException(400, f"Unknown field {attr}")

        return True

    def _parse_sortstr(self, value: str):
        if not value:
            return None

        for colname in value.split(","):
            sort_asc = True
            if colname.startswith("-"):
                colname = colname[1:]
                sort_asc = False

            if self._model_has_attrs(colname):
                # @TODO - support ordering by related fields
                tbl_colname = text(f"{self.model.__tablename__}.{colname}")
                yield asc(tbl_colname) if sort_asc else desc(tbl_colname)

    def _parse_query(self, **kwargs):
        # @TODO - implement _model_has_attrs for local and referenced values
        # @TODO - split up method, reuse in _parse_sortstr

        clauses = []

        for key, value in kwargs.items():
            if "__" in key:
                parts = key.split("__")

                op = parts[-1].upper()
                field_name = parts[-2]
                relations = parts[:-2]

                if len(relations) > 1:
                    raise AioliException(message="Unsupported query depth", status=400)
                elif len(relations) == 1:
                    related_name = relations[0]
                    column = self.model.__related__[related_name].columns[field_name]
                else:
                    column = self.model.__table__.columns[field_name]
            else:
                op = FilterOperator.EXACT.name
                column = self.model.__table__.columns[key]

            try:
                op_attr = FilterOperator[op].value
            except KeyError:
                raise AioliException(
                    message=f"Invalid operator: {op}, available: {[e.name for e in FilterOperator]}",
                    status=400,
                )

            if isinstance(value, orm.models.Model):
                value = value.pk
            elif op in [FilterOperator.CONTAINS.name, FilterOperator.ICONTAINS.name]:
                value = "%" + value + "%"

            clause = getattr(column, op_attr)(value)
            clauses.append(clause)

        if clauses:
            if len(clauses) == 1:
                return clauses[0]
            else:
                return sql.and_(*clauses)

        return None

    async def _get(self, **params):
        join = params.pop("join_related", True)
        limit = params.pop("limit", None)
        sort = params.pop("sort", None)
        offset = params.pop("offset", None)
        query = params.pop("query", None)

        related = self.related if join else []

        qs = orm.models.QuerySet(self.model, select_related=related)
        stmt = qs.build_select_expression().limit(limit).offset(offset)

        if query:
            if isinstance(query, str):
                clauses = [clause.split("=") for clause in query.split(",")]
                stmt = stmt.where(self._parse_query(**dict(clauses)))
            elif isinstance(query, dict):
                stmt = stmt.where(self._parse_query(**query))

        if sort:
            sort_fields = self._parse_sortstr(sort)
            stmt = stmt.order_by(*sort_fields)

        return [
            self.model.from_row(row, select_related=related)
            for row in await self.manager.database.fetch_all(stmt)
        ]

    async def get_many(self, **kwargs):
        return await self._get(**kwargs)

    async def get_one(self, **kwargs):
        pk_value = kwargs.pop("pk", None)
        if pk_value:
            kwargs[self.model.__pkname__] = pk_value

        result = await self._get(limit=2, query=kwargs)

        if len(result) == 0:
            raise NoMatchFound
        elif len(result) > 1:
            raise AioliException(message="Multiple matches for get_one", status=500)

        return result[0]

    async def create(self, **item: dict):
        return await orm.models.QuerySet(self.model).create(**item)

    async def count(self, **kwargs):
        clauses = self._parse_query(**kwargs)
        query = select([func.count()]).select_from(self.model.__table__).where(clauses)
        return await self.manager.database.fetch_val(query)

    async def update(self, record_id, payload):
        record = await self.get_one(pk=record_id)
        await record.update(**payload)
        return record

    async def delete(self, record_id):
        record = await self.get_one(pk=record_id)
        await record.delete()
