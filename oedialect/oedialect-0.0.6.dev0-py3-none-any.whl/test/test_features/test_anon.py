from sqlalchemy.testing import fixtures, config, eq_
from sqlalchemy import Column, INTEGER, Table, select
import sqlalchemy as sa
from sqlalchemy.orm.session import sessionmaker
from ..login import ANON_STRING
class TableCommentTest(fixtures.TablesTest):
    __backend__ = True

    @classmethod
    def define_tables(cls, metadata):
        cls.engine = metadata.bind
        Table("anon_table", metadata,
              Column('id', INTEGER, primary_key=True),
              Column('x', INTEGER)
              )

    @classmethod
    def insert_data(cls):
        config.db.execute(
            cls.tables.anon_table.insert(),
            [
                {'x': 1}
            ]
        )

    def _assert_result(self, select, result):
        eq_(
            config.db.execute(select).fetchall(),
            result
        )

    def test_anon_user(self):
        OED_STRING = 'postgresql+oedialect://{creds}'.format(creds=ANON_STRING)
        engine = sa.create_engine(OED_STRING)
        metadata = sa.MetaData(bind=engine)
        Session = sessionmaker()
        session = Session(bind=engine)
        result = [r for r in session.query(self.tables.anon_table)]
        eq_(result, [(1,1)])
        session.close()
