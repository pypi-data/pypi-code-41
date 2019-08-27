# Copyright 2019 Okera Inc. All Rights Reserved.
#
# Some integration tests against the crawler

# pylint: disable=broad-except
import time
import unittest

from okera import context
from okera.tests import pycerebro_test_common as common

CRAWLER_STATUS_KEY = 'okera.crawler.status'

class CrawlerIntegrationTest(unittest.TestCase):
    def _wait_for_crawler(self, conn, crawler_db, dataset=None, max_sec=15):
        """ Waits for the crawler to find dataset for this crawler

            If dataset is None, then just wait for the crawler to report COMPLETED.
        """
        elapsed_sec = 0
        datasets = None
        while elapsed_sec < max_sec:
            time.sleep(1)
            elapsed_sec += 1
            if dataset:
                datasets = conn.list_dataset_names(crawler_db)
                if (crawler_db + '.' + dataset) in datasets:
                    return datasets
            else:
                params = conn.execute_ddl('DESCRIBE DATABASE %s' % crawler_db)
                for p in params:
                    if p[0] == CRAWLER_STATUS_KEY and p[1] == 'COMPLETED':
                        return conn.list_dataset_names(crawler_db)
        if not datasets:
            datasets = conn.list_dataset_names(crawler_db)
        print("Found datasets: " + str(datasets))
        self.fail('Crawler did not find dataset in time.')

    @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    def test_basic(self, testType=None):
        crawler = 'integration_test'
        crawler_db = '_okera_crawler_' + crawler
        if testType is None:
            location = 's3://cerebrodata-test/tpch-nation-integration-test/'
        elif testType == 'ADLS':
            location = ('adl://okeratestdata.azuredatalakestore.net/cerebrodata-test/' +
                        'tpch-nation-integration-test/')
        else:
            self.fail('Test received invalid testType: ' + testType)
        ctx = context()
        with ctx.connect() as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            self._wait_for_crawler(conn, crawler_db, 'tpch_nation_integration_test')

    @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    def test_not_slow_5k(self):
        # This table has 5K partitions, make sure it finishes reasonably quickly
        location = 's3://cerebrodata-test/part_flat_5000_data_100/'
        # TODO: make this support ADLS when this dataset exists there
        crawler = 'integration_test'
        crawler_db = '_okera_crawler_' + crawler
        ctx = context()
        with ctx.connect() as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            # If it doesn't find it in time, this will fail with a timeout
            # On a dev EC2 vm, this takes ~3 seconds
            self._wait_for_crawler(conn, crawler_db, 'part_flat_5000_data_100', 10)

    @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    def test_flat(self, testType=None):
        crawler = 'integration_test'
        crawler_db = '_okera_crawler_' + crawler
        if testType is None:
            location = 's3://cerebrodata-test/crawler_flat_structure/'
        elif testType == 'ADLS':
            location = ('adl://okeratestdata.azuredatalakestore.net/cerebrodata-test/' +
                        'crawler_flat_structure/')
        else:
            self.fail('Test received invalid testType: ' + testType)
        ctx = context()
        with ctx.connect() as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))

            # This should only find one dataset since flat structures is not the default
            self._wait_for_crawler(conn, crawler_db, None)
            datasets = conn.list_dataset_names(crawler_db)
            self.assertTrue(len(datasets) == 1)
            conn.execute_ddl('DROP TABLE %s.%s' % (crawler_db, 'crawler_flat_structure'))

            # Configure this crawler to accept flat structures
            conn.execute_ddl("ALTER DATABASE %s SET DBPROPERTIES('%s'='%s')" %\
                (crawler_db, 'okera.crawler.single_file_dataset', 'true'))
            conn.execute_ddl("ALTER DATABASE %s SET DBPROPERTIES('%s'='%s')" %\
                (crawler_db, CRAWLER_STATUS_KEY, ''))

            # Crawler should have been retriggered, wait for it, it should now find
            # both datasets
            self._wait_for_crawler(conn, crawler_db, 'atp_csv')
            self._wait_for_crawler(conn, crawler_db, 'topbabynamesbystate_csv')

    @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    def test_empty(self, testType=None):
        crawler = 'test_empty'
        crawler_db = '_okera_crawler_' + crawler
        if testType is None:
            location = 's3://cerebrodata-test/empty/'
        elif testType == 'ADLS':
            location = ('adl://okeratestdata.azuredatalakestore.net/' +
                        'cerebrodata-test/empty_folder/')
        else:
            self.fail('Test received invalid testType: ' + testType)
        ctx = context()
        with ctx.connect() as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            contents = self._wait_for_crawler(conn, crawler_db, None)

        if contents:
            self.fail('Directory was not empty, location : ' + location)

    @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    def test_hidden_file(self, testType=None):
        crawler = 'test_hidden_file'
        crawler_db = '_okera_crawler_' + crawler
        if testType is None:
            location = 's3://cerebrodata-test/hidden_files_only/'
        elif testType == 'ADLS':
            location = ('adl://okeratestdata.azuredatalakestore.net/' +
                        'cerebrodata-test/hidden_file/')
        else:
            self.fail('Test received invalid testType: ' + testType)
        ctx = context()
        with ctx.connect() as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            contents = self._wait_for_crawler(conn, crawler_db, None)

        if contents:
            self.fail('Directory was not empty or hidden file found, location : '
                      + location)

    @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    def test_bad_path_good_scheme(self, testType=None):
        caught = None
        crawler = 'test_bad_path_good_scheme'
        crawler_db = '_okera_crawler_' + crawler
        bucket = 'thispathdoesnotexistcerebro'
        if testType is None:
            location = ('s3://%s/' % bucket)
        elif testType == 'ADLS':
            location = ('adl://%s.azuredatalakestore.net/'% bucket)
        ctx = context()
        with ctx.connect() as conn:
            try:
                conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
                conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            except Exception as e:
                if "is not accessible" not in str(e) and "does not exist" not in str(e):
                    self.fail("Exception did not match expected. Ex encountered: "
                              + str(e))
                else:
                    caught = True
            if(not caught):
                self.fail("No exception raised, expected TRecordServiceException")

    @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    def test_null_path(self):
        crawler = 'test_null_path'
        caught = None
        crawler_db = '_okera_crawler' + crawler
        ctx = context()
        with ctx.connect() as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            try:
                conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, None))
            except Exception as e:
                if "is not accessible" not in str(e):
                    self.fail("Exception did not match expected. Ex encountered: "
                              + str(e))
                else:
                    caught = True

            if not caught:
                self.fail("No exception raised, expected TRecordServiceException")

    @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    def test_bad_scheme(self):
        caught = None
        crawler = 'test_bad_scheme'
        crawler_db = '_okera_crawler' + crawler
        location = 'foo://bucket/path'
        ctx = context()
        with ctx.connect() as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            try:
                conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            except Exception as e:
                if "No FileSystem for scheme" not in str(e):
                    self.fail("Exception did not match expected. Ex encountered: "
                              + str(e))
                else:
                    caught = True
            if not caught:
                self.fail("No exception raised, expected TRecordServiceException")

    @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    def test_crawl_partitioned(self, testType=None):
        crawler = 'test_crawl_partitioned'
        crawler_db = '_okera_crawler_' + crawler
        if testType is None:
            location = 's3://cerebrodata-test/partitions-test2/'
        elif testType == 'ADLS':
            location = ('adl://okeratestdata.azuredatalakestore.net/' +
                        'cerebrodata-test/partitions-test/')
        else:
            self.fail('Test received invalid testType: ' + testType)
        ctx = context()
        with ctx.connect() as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            contents = self._wait_for_crawler(conn, crawler_db, None, 30)

        if len(contents) != 2:
            self.fail("Did not find 2 datasets at location: " + location)

    @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    def test_crawl_already_registered(self, testType=None):
        crawler = 'test_crawl_already_registered'
        crawler_db = '_okera_crawler_' + crawler
        if testType is None:
            location = 's3://cerebrodata-test/tpch_nation/'
        elif testType == 'ADLS':
            location = ('adl://okeratestdata.azuredatalakestore.net/'
                        'cerebrodata-test/tpch_nation/')
        else:
            self.fail('Test received invalid testType: ' + testType)
        ctx = context()
        with ctx.connect() as conn:
            if testType is None:
                conn.execute_ddl("CREATE EXTERNAL TABLE IF NOT EXISTS"
                                 "`default`.`tpch_nation_s3`(s smallint"
                                 ", n string, t smallint, d string) LOCATION '%s'"
                                 % location)
            elif testType == 'ADLS':
                conn.execute_ddl("CREATE EXTERNAL TABLE IF NOT EXISTS"
                                 "`default`.`tpch_nation_adls`(s smallint"
                                 ", n string, t smallint, d string) LOCATION '%s'"
                                 % location)
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            contents = self._wait_for_crawler(conn, crawler_db, None)

        if contents:
            print(str(contents))
            self.fail("Found unregistered dataset when should have found none: " +
                      location)

    @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    def test_crawl_duplicate_paths(self, testType=None):
        crawler1 = 'test_crawl_duplicate_paths_1'
        crawler1_db = '_okera_crawler_' + crawler1
        crawler2 = 'test_crawl_duplicate_paths_2'
        crawler2_db = '_okera_crawler_' + crawler2
        if testType is None:
            location = 's3://cerebrodata-test/alltypes-parquet/'
        elif testType == 'ADLS':
            location = ('adl://okeratestdata.azuredatalakestore.net/'
                        'cerebrodata-test/alltypes-parquet/')
        else:
            self.fail('Test received invalid testType: ' + testType)
        ctx = context()
        with ctx.connect() as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler1_db)
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler2_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler1, location))
            contents1 = self._wait_for_crawler(conn, crawler1_db, None)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler2, location))
            contents2 = self._wait_for_crawler(conn, crawler2_db, None)

            contents1 = [ds.split(".")[1] for ds in contents1]
            contents2 = [ds.split(".")[1] for ds in contents2]

        self.assertEqual(contents1, contents2)

    @staticmethod
    def __get_columns(dataset):
        cols = []
        partition_cols = []
        for c in dataset.schema.cols:
            if c.hidden:
                continue
            if c.is_partitioning_col:
                partition_cols.append(c.name)
            else:
                cols.append(c.name)
        return cols, partition_cols

    @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    def test_data_partition_col_dup(self):
        # This dataset has the same column name in the partition path and data file.
        # We want to ignore the column in the data file.
        crawler = 'e2e_test'
        crawler_db = '_okera_crawler_' + crawler
        location = 's3://cerebro-test-itay/lake4/partitioned2/'

        ctx = context()
        with ctx.connect() as conn:
            # Default crawler allows duplicates
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            self._wait_for_crawler(conn, crawler_db, 'partitioned2')
            dataset = conn.list_datasets(crawler_db, name='partitioned2')
            cols, partition_cols = self.__get_columns(dataset[0])
            self.assertTrue('str2' in cols)
            self.assertTrue('str2' in partition_cols)
            show = conn.execute_ddl(
                'show create table %s.%s' % (crawler_db, 'partitioned2'))[0][0]
            self.assertEqual(2, show.count('str2 STRING'), msg=show)

            # Configure this crawler to ignore duplicates
            conn.execute_ddl("DROP TABLE %s.%s" % (crawler_db, 'partitioned2'))
            conn.execute_ddl("ALTER DATABASE %s SET DBPROPERTIES('%s'='%s')" %\
                (crawler_db, 'okera.allow.partition_cols_in_data', 'true'))
            conn.execute_ddl("ALTER DATABASE %s SET DBPROPERTIES('%s'='%s')" %\
                (crawler_db, CRAWLER_STATUS_KEY, ''))
            self._wait_for_crawler(conn, crawler_db, 'partitioned2')
            dataset = conn.list_datasets(crawler_db, name='partitioned2')
            cols, partition_cols = self.__get_columns(dataset[0])

            # str2 should not be in cols now, only in partition cols
            self.assertTrue('str2' not in cols)
            self.assertTrue('str2' in partition_cols)
            show = conn.execute_ddl(
                'show create table %s.%s' % (crawler_db, 'partitioned2'))[0][0]
            self.assertEqual(1, show.count('str2 STRING'), msg=show)

    @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    def test_crawler_no_suffix(self):
        # Crawl a directory where the datasets don't have file suffixes and make
        # sure we can find them another way.
        crawler = 'e2e_test'
        crawler_db = '_okera_crawler_' + crawler
        location = 's3://okera-ui/autotagger/no-postfix'

        ctx = context()
        with ctx.connect() as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            self._wait_for_crawler(conn, crawler_db)

            dataset = conn.list_datasets(crawler_db, name='csv')[0]
            self.assertEqual("TEXT", dataset.table_format)
            dataset = conn.list_datasets(crawler_db, name='parquet')[0]
            self.assertEqual("PARQUET", dataset.table_format)
            dataset = conn.list_datasets(crawler_db, name='avro')[0]
            self.assertEqual("AVRO", dataset.table_format)
            dataset = conn.list_datasets(crawler_db, name='json')[0]
            self.assertEqual("JSON", dataset.table_format)

    @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    def test_crawler_tsv(self):
        # Crawl a directory where the datasets don't have file suffixes and make
        # sure we can find them another way.
        crawler = 'e2e_test'
        crawler_db = '_okera_crawler_' + crawler
        location = 's3://cerebro-test-kevin/dea_pain_pills/'

        ctx = context()
        with ctx.connect() as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            self._wait_for_crawler(conn, crawler_db)

            dataset = conn.list_datasets(crawler_db, name='dea_pain_pills')[0]
            self.assertEqual("TEXT", dataset.table_format)
            self.assertEqual(42, len(dataset.schema.cols))

    @unittest.skipIf(common.TEST_LEVEL != "ci", "Only running at CI level.")
    def test_root_crawler(self):
        # Crawl the root test bucket, this can take a while.
        crawler = 'e2e_test'
        crawler_db = '_okera_crawler_' + crawler
        location = 's3://cerebrodata-test/'

        ctx = context()
        with ctx.connect() as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            self._wait_for_crawler(conn, crawler_db, max_sec=400)
            datasets = conn.list_dataset_names(crawler_db)
            self.assertTrue(len(datasets) > 200)


    # # TODO: for the following tests we need a way to determine if cluster is configured
    # # with ADLS credentials or not and skip accordingly
    # @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    # def test_basic_adls(self):
    #     self.test_basic(testType='ADLS')

    # @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    # def test_flat_adls(self):
    #     self.test_flat(testType='ADLS')

    # @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    # def test_empty_adls(self):
    #     self.test_empty(testType='ADLS')

    # @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    # def test_hidden_file_adls(self):
    #     self.test_hidden_file(testType='ADLS')

    # # This test takes a long time to execute. See DAS-3203 for details.
    # @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    # def test_bad_path_good_scheme_adls(self):
    #     self.test_bad_path_good_scheme(testType='ADLS')

    # @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    # def test_crawl_partitioned_adls(self):
    #     self.test_crawl_partitioned(testType='ADLS')

    # @unittest.skipIf(common.TEST_LEVEL == "smoke", "Skipping at unit test level")
    # def test_crawl_already_registered_adls(self):
    #     self.test_crawl_already_registered(testType='ADLS')

if __name__ == "__main__":
    unittest.main()
