import td_pyspark
from pyspark.sql import SparkSession
import unittest
from datetime import datetime

class TDPySparkTest(unittest.TestCase):
    SAMPLE_TABLE = "sample_datasets.www_access"

    @classmethod
    def setUpClass(self):
        builder = SparkSession.builder.appName("td-pyspark-test")
        self.td = td_pyspark.TDSparkContextBuilder(builder)\
            .build()

        self.test_db_name = 'td_pyspark_test_{}'.format(str(datetime.now().timestamp()).replace('.', '_'))
        self.td.create_database_if_not_exists(self.test_db_name)

    @classmethod
    def tearDownClass(self):
        self.td.drop_database_if_exists(self.test_db_name)
        self.td.spark.stop()

    def get_source_sample(self):
        return self.td.table(TDPySparkTest.SAMPLE_TABLE).df().limit(3)

    def create_or_refresh(self, table_name):
        target_table = self.td.table(table_name)
        target_table.drop_if_exists()
        target_table.create_if_not_exists()
        return target_table

    def test_show(self):
        df = self.td.table("sample_datasets.www_access") \
            .within("+2d/2014-10-04")\
            .df()
        df.show()

    def test_read(self):
        df = self.get_source_sample()
        self.assertEqual(df.count(), 3)
        self.assertEqual(len(df.schema), 9)

    def test_exists(self):
        self.assertTrue(self.td.db("sample_datasets").exists())
        self.assertTrue(self.td.db(self.test_db_name).exists())

    def test_insert(self):
        table_name = "{}.test_insert".format(self.test_db_name)
        target_table = self.create_or_refresh(table_name)
        df = self.get_source_sample()
        self.td.insert_into(df, table_name)

        count = target_table.df().count()
        self.assertEqual(count, 3)

    def test_create(self):
        table_name = "{}.test_create".format(self.test_db_name)
        target_table = self.create_or_refresh(table_name)
        df = self.get_source_sample()
        self.td.create_or_replace(df, table_name)

        count = target_table.df().count()
        self.assertEqual(count, 3)

    def test_create_udp_l(self):
        table_name = "{}.test_create_udp_l".format(self.test_db_name)
        target_table = self.create_or_refresh(table_name)
        df = self.get_source_sample()
        self.td.create_udp_l(table_name, 'code')
        self.td.insert_into(df, table_name)

        count = target_table.df().count()
        self.assertEqual(count, 3)

    def test_create_udp_s(self):
        table_name = "{}.test_create_udp_s".format(self.test_db_name)
        target_table = self.create_or_refresh(table_name)
        df = self.get_source_sample()
        self.td.create_udp_s(table_name, 'path')
        self.td.insert_into(df, table_name)

        count = target_table.df().count()
        self.assertEqual(count, 3)

    def test_supported_site(self):
        endpoints = td_pyspark.TDSparkContextBuilder.ENDPOINTS
        self.assertTrue('us' in endpoints)
        self.assertTrue('jp' in endpoints)
        self.assertTrue('eu' in endpoints)

    def test_presto(self):
        df = self.td.presto('select * from sample_datasets.www_access limit 3')
        self.assertTrue(len(df.schema), 9)
        self.assertTrue(df.count(), 3)


if __name__ == '__main__':
    unittest.main()