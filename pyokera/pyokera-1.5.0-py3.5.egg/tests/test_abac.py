# Copyright 2019 Okera Inc. All Rights Reserved.
#
# Some integration tests for ABAC
#
# pylint: disable=too-many-arguments
# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods

import unittest

from okera import context, _thrift_api

TEST_DB = 'abac_test_db'
TEST_DB2 = 'abac_test_db2'
TEST_TBL = 'tbl'
TEST_TBL2 = 'tbl2'
TEST_DB_DROP = 'drop_db1'
TEST_TBL_DROP = 'drop_table1'
TEST_VIEW = 'v'
TEST_ROLE = 'abac_test_role'
TEST_USER = 'abac_test_user'
TEST_ROLE_DROP = 'abac_test_role_drop'
TEST_USER_DROP = 'abac_test_user_drop'

class AbacTest(unittest.TestCase):
    @staticmethod
    def __grant_abac_db(conn, db, namespace, key):
        conn.execute_ddl(
            'GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE(%s.%s) TO ROLE %s' %\
            (db, namespace, key, TEST_ROLE))

    @staticmethod
    def __grant_abac_tbl(conn, db, tbl, namespace, key):
        conn.execute_ddl(
            'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE(%s.%s) TO ROLE %s' %\
            (db, tbl, namespace, key, TEST_ROLE))

    @staticmethod
    def __revoke_abac_db(conn, db, namespace, key):
        conn.execute_ddl(
            'REVOKE SELECT ON DATABASE %s HAVING ATTRIBUTE(%s.%s) FROM ROLE %s' %\
            (db, namespace, key, TEST_ROLE))

    @staticmethod
    def __revoke_abac_tbl(conn, db, tbl, namespace, key):
        conn.execute_ddl(
            'REVOKE SELECT ON TABLE %s.%s HAVING ATTRIBUTE(%s.%s) FROM ROLE %s' %\
            (db, tbl, namespace, key, TEST_ROLE))

    @staticmethod
    def __show_grant_abac_role(conn):
        return conn.execute_ddl('SHOW GRANT ROLE %s' % (TEST_ROLE))

    @staticmethod
    def __ddl_count(conn, sql):
        return len(conn.execute_ddl(sql))

    @staticmethod
    def __visible_cols(cols):
        result = []
        for c in cols:
            if c.hidden:
                continue
            result.append(c)
        return result

    def __verify_tbl_access(self, conn, db, tbl, num_cols, has_db_access=False,
                            skip_metadata_check=False):
        """ Verifies the current connect has access to num_cols on this table

            FIXME(BUG): skip_metadata_check should be removed (and always True). It is
            skipping due to existing bugs.
        """
        if num_cols == 0:
            for ddl in ['describe %s.%s', 'describe formatted %s.%s']:
                with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                    print(conn.execute_ddl(ddl % (db, tbl)))
                self.assertTrue('does not have privilege' in str(ex_ctx.exception))

            if has_db_access:
                # User has access to DB, make sure table does not show up in list
                self.assertTrue('%s.%s' %(db, tbl) not in conn.list_dataset_names(db))
                names = conn.list_dataset_names(db)
                self.assertFalse('%s.%s' %(db, tbl) in names, msg=str(names))
            else:
                # Doesn't have database access, ensure listing tables in it fails
                with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                    print("Listing datasets in: " + db)
                    print(conn.list_dataset_names(db))
                self.assertTrue('does not have privilege' in str(ex_ctx.exception))

                datasets = conn.list_datasets(db)
                self.assertEqual(len(datasets), 0, msg=str(datasets))

                for ddl in ['describe database %s', 'show tables in %s']:
                    with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                        print(conn.execute_ddl(ddl % db))
                    self.assertTrue('does not have privilege' in str(ex_ctx.exception))

                if not skip_metadata_check:
                    dbs = conn.list_databases()
                    self.assertFalse(TEST_DB in dbs, msg=str(dbs))
        else:
            dbs = conn.list_databases()
            self.assertTrue(db in dbs, msg=str(dbs))
            names = conn.list_dataset_names(db)
            self.assertTrue('%s.%s' %(db, tbl) in names, msg=str(names))
            datasets = conn.list_datasets(db, name=tbl)
            self.assertEqual(len(datasets), 1)
            cols = self.__visible_cols(conn.list_datasets(db, name=tbl)[0].schema.cols)
            self.assertEqual(len(cols), num_cols)

            datasets = conn.list_datasets(db)
            self.assertTrue(len(datasets) >= 1, msg=str(datasets))

    @classmethod
    def setUpClass(cls):
        """ Initializes one time state that is shared across test cases. This is used
            to speed up the tests. State that can be shared across (but still stable)
            should be here instead of __cleanup()."""
        super(AbacTest, cls).setUpClass()
        ctx = context()
        with ctx.connect() as conn:
            conn.delete_attribute('abac_test', 'v1')
            conn.create_attribute('abac_test', 'v1')
            conn.delete_attribute('abac_test', 'v2')
            conn.create_attribute('abac_test', 'v2')
            conn.delete_attribute('abac_test', 'v3')
            conn.create_attribute('abac_test', 'v3')
            conn.delete_attribute('abac_test', 'pii')
            conn.create_attribute('abac_test', 'pii')
            conn.delete_attribute('abac_test', 'email')
            conn.create_attribute('abac_test', 'email')
            conn.delete_attribute('abac_test', 'sales')
            conn.create_attribute('abac_test', 'sales')
            conn.delete_attribute('abac_test', 'marketing')
            conn.create_attribute('abac_test', 'marketing')

    @staticmethod
    def __cleanup(conn, dbs=None):
        """ Cleanups all the test state used in this test to "reset" the catalog.
            dbs can be specified to do the initialize over multiple databases.
            This can be used for tests that use multiple dbs (but makes the test
            take longer). By default, only load TEST_DB.
        """
        conn.execute_ddl("DROP ROLE IF EXISTS %s" % TEST_ROLE)
        conn.execute_ddl("CREATE ROLE %s" % TEST_ROLE)
        conn.execute_ddl("GRANT ROLE %s to GROUP %s" % (TEST_ROLE, TEST_USER))

        # Always drop both to prevent state from leaking
        conn.execute_ddl("DROP DATABASE IF EXISTS %s CASCADE" % TEST_DB)
        conn.execute_ddl("DROP DATABASE IF EXISTS %s CASCADE" % TEST_DB2)

        if not dbs:
            dbs = [TEST_DB]

        for db in dbs:
            conn.execute_ddl("CREATE DATABASE %s" % db)
            conn.execute_ddl("CREATE TABLE %s.%s(col1 int, col2 int, col3 int)" % \
                (db, TEST_TBL))
            conn.execute_ddl("CREATE TABLE %s.%s(col1 int, col2 int, col3 int)" % \
                (db, TEST_TBL2))
            conn.execute_ddl("CREATE VIEW %s.%s AS SELECT * FROM %s.%s" % \
                (db, TEST_VIEW, TEST_DB, TEST_TBL))

    @staticmethod
    def __revoke(conn, sql):
        """ Revokes a grant, transforming a GRANT statement to its corresponding REVOKE"""
        sql = sql.lower()
        sql = sql.replace('grant', 'revoke')
        sql = sql.replace('to role', 'from role')
        conn.execute_ddl(sql)

    @staticmethod
    def __fixture1(conn):
        """ Creates a representative test fixture. This will:
              Tag TEST_DB with department sales
              Tag TEST_DB2 with department marketing.
              Tag TEST_DB2.TEST_TBL with department sales.
              Tag some columns with pii tags, and some with another tag and a third
              column with no tags.
        """
        conn.assign_attribute('abac_test', 'sales', TEST_DB)
        conn.assign_attribute('abac_test', 'marketing', TEST_DB2)
        conn.assign_attribute('abac_test', 'sales', TEST_DB2, TEST_TBL)

        for db in [TEST_DB, TEST_DB2]:
            conn.assign_attribute('abac_test', 'pii', db, TEST_TBL, 'col1')
            conn.assign_attribute('abac_test', 'pii', db, TEST_TBL2, 'col1')
            conn.assign_attribute('abac_test', 'pii', db, TEST_VIEW, 'col1')
            conn.assign_attribute('abac_test', 'v1', db, TEST_TBL, 'col2')
            conn.assign_attribute('abac_test', 'v1', db, TEST_TBL2, 'col2')
            conn.assign_attribute('abac_test', 'v1', db, TEST_VIEW, 'col2')

    # Tests that grants are case insensitive for catalog objects, attributes and exprs.
    def test_case_insensitive_exprs(self):
        ctx = context()
        with ctx.connect() as conn:
            self.__cleanup(conn)
            # Grant with all lower case
            conn.execute_ddl(
                'GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE(%s.%s) TO ROLE %s' %\
                (TEST_DB, 'abac_test', 'v1', TEST_ROLE))

            # Try some duplicates, they should all fail
            with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                conn.execute_ddl(
                    'GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE(%s) TO ROLE %s' %\
                    (TEST_DB, 'abac_test.v1', TEST_ROLE))
            self.assertTrue('Grant already exists' in str(ex_ctx.exception))
            with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                conn.execute_ddl(
                    'GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE(%s) TO ROLE %s' %\
                    (TEST_DB, 'abac_TEST.v1', TEST_ROLE))
            self.assertTrue('Grant already exists' in str(ex_ctx.exception))
            with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                conn.execute_ddl(
                    'GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE(%s) TO ROLE %s' %\
                    (TEST_DB.upper(), 'not abac_test.v1', TEST_ROLE))
            self.assertTrue('Another grant with' in str(ex_ctx.exception))
            with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                conn.execute_ddl(
                    'GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE(%s.%s) TO ROLE %s' %\
                    (TEST_DB.upper(), 'Abac_test', 'v1', TEST_ROLE))
            self.assertTrue('Grant already exists' in str(ex_ctx.exception))
            with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                conn.execute_ddl(
                    'GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE(%s) TO ROLE %s' %\
                    (TEST_DB.upper(), 'NOT Abac_test.V1', TEST_ROLE))
            self.assertTrue('Another grant with' in str(ex_ctx.exception))
            with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                conn.execute_ddl(
                    'GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE(%s.%s) TO ROLE %s' %\
                    (TEST_DB.upper(), 'Abac_test', 'V1', TEST_ROLE))
            self.assertTrue('Grant already exists' in str(ex_ctx.exception))

    def test_in_print(self):
        ctx = context()
        with ctx.connect() as conn:
            self.__cleanup(conn)
            # Grant with all lower case
            conn.execute_ddl(
                'GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE IN(%s.%s) TO ROLE %s' %\
                (TEST_DB, 'abac_test', 'v1', TEST_ROLE))
            conn.execute_ddl(
                'GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE NOT IN(%s.%s) TO ROLE %s' %\
                (TEST_DB, 'abac_test', 'v2', TEST_ROLE))

            result = conn.execute_ddl('SHOW GRANT ROLE %s' % TEST_ROLE)
            self.assertEqual(2, len(result))
            for r in result:
                expr = r[6]
                self.assertFalse('null' in expr)

    def test_db(self):
        ctx = context()
        with ctx.connect() as conn:
            self.__cleanup(conn)

            # Admin should see it but test user should not
            self.assertTrue(TEST_DB in conn.list_databases())
            ctx.enable_token_auth(token_str=TEST_USER)
            self.assertTrue('okera_sample' in conn.list_databases())
            self.assertFalse(TEST_DB in conn.list_databases())

            # Switch back to admin and assign abac_test.v1 to this db
            ctx.disable_auth()
            self.__grant_abac_db(conn, TEST_DB, 'abac_test', 'v1')

            # Test user should not have access to this DB but currently does.
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 0)

            # Assign the attribute
            ctx.disable_auth()
            conn.assign_attribute('abac_test', 'v1', TEST_DB)

            # List databases again, test user should have access now
            self.assertTrue(TEST_DB in conn.list_databases())
            ctx.enable_token_auth(token_str=TEST_USER)
            self.assertTrue('okera_sample' in conn.list_databases())
            self.assertTrue(TEST_DB in conn.list_databases())

            # Should have full access to both tables
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 3)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 3)
            self.__verify_tbl_access(conn, TEST_DB, TEST_VIEW, 3)

    def test_tbl_view(self):
        ctx = context()
        with ctx.connect() as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                # Admin should see it but test user should not
                self.assertTrue(
                    '%s.%s' %(TEST_DB, ds) in conn.list_dataset_names(TEST_DB))
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0)

                # Switch back to admin and assign abac_test.v1 to this dataset
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'v1', TEST_DB, ds)
                self.__grant_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'v1')
                # List tables again, test user should have access now
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 3)

                # Unassign the attribute, testuser should not see it anymore
                ctx.disable_auth()
                conn.unassign_attribute('abac_test', 'v1', TEST_DB, ds)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0)

                # Assign the attribute again but revoke the grant, should not have access
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'v1', TEST_DB, ds)
                self.__revoke_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'v1')
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0)

    def test_col(self):
        ctx = context()
        with ctx.connect() as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                # Verify no access to start
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 0)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0)
                self.__verify_tbl_access(conn, TEST_DB, TEST_VIEW, 0)

                # Switch back to admin and assign abac_test.v1 to just one column and
                # issue the grant.
                ctx.disable_auth()
                self.__grant_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'v1')
                conn.assign_attribute('abac_test', 'v1', TEST_DB, ds, 'col1')
                self.assertTrue(
                    '%s.%s' %(TEST_DB, ds) in conn.list_dataset_names(TEST_DB))

                # Verify user can just see one column on this one table
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 1)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0, has_db_access=True)

                # Assign attribute to other column
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'v1', TEST_DB, ds, 'col2')

                # Now should be able to see both.
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 2)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0, has_db_access=True)

                # Unassign one attribute
                ctx.disable_auth()
                conn.unassign_attribute('abac_test', 'v1', TEST_DB, ds, 'col1')
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 1)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0, has_db_access=True)

                # Unassign other
                ctx.disable_auth()
                conn.unassign_attribute('abac_test', 'v1', TEST_DB, ds, 'col2')
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0)

                # Revoke the grant
                ctx.disable_auth()
                self.__revoke_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'v1')
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0)

    def test_attr(self):
        ctx = context()
        with ctx.connect() as conn:
            for expr in ['abac_test.v1', 'in(abac_test.v1)',
                         'in(abac_test.v2, abac_test.v1)']:
                for ds in [TEST_TBL, TEST_VIEW]:
                    ctx.disable_auth()
                    self.__cleanup(conn)

                    # No tags, user can none
                    conn.execute_ddl(
                        'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE %s TO ROLE %s' %\
                        (TEST_DB, ds, expr, TEST_ROLE))
                    ctx.disable_auth()
                    ctx.enable_token_auth(token_str=TEST_USER)
                    self.__verify_tbl_access(conn, TEST_DB, ds, 0)

                    # Assign attribute to one column, user can see 1
                    ctx.disable_auth()
                    conn.assign_attribute('abac_test', 'v1', TEST_DB, ds, 'col1')
                    ctx.enable_token_auth(token_str=TEST_USER)
                    self.__verify_tbl_access(conn, TEST_DB, ds, 1)

                    # Assign attribute to second column, user can see 2
                    ctx.disable_auth()
                    conn.assign_attribute('abac_test', 'v1', TEST_DB, ds, 'col2')
                    ctx.enable_token_auth(token_str=TEST_USER)
                    self.__verify_tbl_access(conn, TEST_DB, ds, 2)

                    # Assign attribute to last column, user can see all 3
                    ctx.disable_auth()
                    conn.assign_attribute('abac_test', 'v1', TEST_DB, ds, 'col3')
                    ctx.enable_token_auth(token_str=TEST_USER)
                    self.__verify_tbl_access(conn, TEST_DB, ds, 3)

    def test_not(self):
        ctx = context()
        with ctx.connect() as conn:
            for expr in ['not abac_test.v1', 'not in(abac_test.v1)',
                         'not in(abac_test.v2, abac_test.v1)',
                         'not not not abac_test.v1']:
                for ds in [TEST_TBL, TEST_VIEW]:
                    ctx.disable_auth()
                    self.__cleanup(conn)

                    # No tags, user can see all 3
                    conn.execute_ddl(
                        'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE %s TO ROLE %s' %\
                        (TEST_DB, ds, expr, TEST_ROLE))
                    ctx.enable_token_auth(token_str=TEST_USER)
                    self.__verify_tbl_access(conn, TEST_DB, ds, 3)

                    # Assign attribute to one column, user can see 2
                    ctx.disable_auth()
                    conn.assign_attribute('abac_test', 'v1', TEST_DB, ds, 'col1')
                    ctx.enable_token_auth(token_str=TEST_USER)
                    self.__verify_tbl_access(conn, TEST_DB, ds, 2)

                    # Assign attribute to second column, user can see 1
                    ctx.disable_auth()
                    conn.assign_attribute('abac_test', 'v1', TEST_DB, ds, 'col2')
                    ctx.enable_token_auth(token_str=TEST_USER)
                    self.__verify_tbl_access(conn, TEST_DB, ds, 1)

                    # Assign attribute to last column, user cannot see
                    ctx.disable_auth()
                    conn.assign_attribute('abac_test', 'v1', TEST_DB, ds, 'col3')
                    ctx.enable_token_auth(token_str=TEST_USER)
                    self.__verify_tbl_access(conn, TEST_DB, ds, 0)

    # Verify abac privileges for role are removed when role is dropped
    def test_drop_role(self):
        ctx = context()
        with ctx.connect() as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                # grant attribute privileges to role
                conn.assign_attribute('abac_test', 'v1', TEST_DB)
                self.__grant_abac_db(conn, TEST_DB, 'abac_test', 'v1')
                self.__grant_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'v1')

                # Ensure 2 privileges
                result = self.__show_grant_abac_role(conn)
                self.assertEqual(len(result), 2)

                conn.execute_ddl("DROP ROLE %s" % TEST_ROLE)
                conn.execute_ddl("CREATE ROLE %s" % TEST_ROLE)

                # Ensure 0 privileges
                result = self.__show_grant_abac_role(conn)
                self.assertEqual(len(result), 0)
                conn.execute_ddl("DROP ROLE %s" % TEST_ROLE)

    def test_show(self):
        ctx = context()
        with ctx.connect() as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)
                admin_before_count = self.__ddl_count(
                    conn, 'SHOW GRANT ATTRIBUTE abac_test.v1 ON CATALOG')
                self.assertEqual(0, self.__ddl_count(
                    conn, 'SHOW GRANT ATTRIBUTE abac_test.v1 ON DATABASE %s' % TEST_DB))
                self.assertEqual(0, self.__ddl_count(
                    conn, 'SHOW GRANT ATTRIBUTE abac_test.v1 ON TABLE %s.%s' % \
                        (TEST_DB, ds)))
                self.assertEqual(0, self.__ddl_count(
                    conn, 'SHOW GRANT ROLE %s ON CATALOG' % TEST_ROLE))

                # Issue some grants, make sure they show correctly
                self.__grant_abac_db(conn, TEST_DB, 'abac_test', 'v1')
                self.__grant_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'v1')

                self.assertEqual(admin_before_count + 2, self.__ddl_count(
                    conn, 'SHOW GRANT ATTRIBUTE abac_test.v1 ON CATALOG'))
                self.assertEqual(2, self.__ddl_count(
                    conn, 'SHOW GRANT ATTRIBUTE abac_test.v1 ON DATABASE %s' % TEST_DB))
                self.assertEqual(1, self.__ddl_count(
                    conn, 'SHOW GRANT ATTRIBUTE abac_test.v1 ON TABLE %s.%s' % \
                    (TEST_DB, ds)))
                self.assertEqual(
                    self.__ddl_count(conn, 'SHOW GRANT ROLE %s' % TEST_ROLE), 2)
                self.assertEqual(2, self.__ddl_count(
                    conn, 'SHOW GRANT ROLE %s ON CATALOG' % TEST_ROLE))
                self.assertEqual(2, self.__ddl_count(
                    conn, 'SHOW GRANT ROLE %s ON DATABASE %s' % (TEST_ROLE, TEST_DB)))
                self.assertEqual(1, self.__ddl_count(
                    conn, 'SHOW GRANT ROLE %s ON TABLE %s.%s' % \
                    (TEST_ROLE, TEST_DB, ds)))
                self.assertEqual(0, self.__ddl_count(
                    conn, 'SHOW GRANT ROLE %s ON DATABASE %s' % \
                    (TEST_ROLE, 'okera_sample')))
                self.assertEqual(0, self.__ddl_count(
                    conn, 'SHOW GRANT ROLE %s ON TABLE %s.%s' % \
                    (TEST_ROLE, 'okera_sample', 'users')))

    def test_show_multiple_grants(self):
        ctx = context()
        with ctx.connect() as conn:
            for ds in [TEST_TBL]:
                ctx.disable_auth()
                self.__cleanup(conn)

                self.__grant_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'v1')
                self.__grant_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'v2')
                self.__grant_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'v3')
                self.__grant_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'sales')
                self.__grant_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'marketing')

                self.assertEqual(5, self.__ddl_count(
                    conn, 'SHOW GRANT ROLE %s ON TABLE %s.%s' % \
                    (TEST_ROLE, TEST_DB, ds)))

    def test_literal_expression(self):
        ctx = context()
        with ctx.connect() as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                # Attribute expression without '='
                conn.execute_ddl(
                    'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE(%s.%s) TO ROLE %s' %\
                    (TEST_DB, ds, 'abac_test', 'v1', TEST_ROLE))
                self.assertEqual(1, self.__ddl_count(
                    conn, 'SHOW GRANT ROLE %s ON TABLE %s.%s' % \
                    (TEST_ROLE, TEST_DB, ds)))
                conn.assign_attribute('abac_test', 'v1', TEST_DB, ds)

                # List tables as test user
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 3)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0, has_db_access=True)

                # Not expression
                ctx.disable_auth()
                conn.execute_ddl(
                    'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE(!%s.%s) TO ROLE %s' %\
                    (TEST_DB, TEST_TBL2, 'abac_test', 'v2', TEST_ROLE))
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 3)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 3)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 3)

                # Revoke one of them
                ctx.disable_auth()
                conn.execute_ddl(
                    'REVOKE SELECT ON TABLE %s.%s HAVING ATTRIBUTE(%s.%s) FROM ROLE %s' %\
                    (TEST_DB, ds, 'abac_test', 'v1', TEST_ROLE))
                self.assertEqual(0, self.__ddl_count(
                    conn, 'SHOW GRANT ROLE %s ON TABLE %s.%s' % \
                    (TEST_ROLE, TEST_DB, ds)))
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0, has_db_access=True)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 3)

                # Revoke other one
                ctx.disable_auth()
                conn.execute_ddl(
                    ('REVOKE SELECT ON TABLE %s.%s HAVING ATTRIBUTE(!%s.%s) ' +\
                    'FROM ROLE %s') %\
                    (TEST_DB, TEST_TBL2, 'abac_test', 'v2', TEST_ROLE))
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0)

    def test_table_column_and_not_and(self):
        ctx = context()
        with ctx.connect() as conn:
            self.__cleanup(conn)

            # Grant with and AND of ORs
            conn.execute_ddl(
                'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE(%s) TO ROLE %s' %\
                (TEST_DB, TEST_TBL,
                 'abac_test.v1=true and (abac_test.v2 != true and abac_test.v3 != true)',
                 TEST_ROLE))

            # Assign v1, should see both columns
            conn.assign_attribute('abac_test', 'v1', TEST_DB, TEST_TBL)
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 3)

            # Tag one of the columns with v2, it should be hidden now
            ctx.disable_auth()
            conn.assign_attribute('abac_test', 'v2', TEST_DB, TEST_TBL, 'col1')
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 2)

            # Tag the other column with the other tag, both should be hidden
            ctx.disable_auth()
            conn.assign_attribute('abac_test', 'v3', TEST_DB, TEST_TBL, 'col2')
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 1)

    def test_table_column_and_or(self):
        ctx = context()
        with ctx.connect() as conn:
            self.__cleanup(conn)

            # Assign abac_test.v1 to this table
            conn.execute_ddl(
                'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE(%s) TO ROLE %s' %\
                (TEST_DB, TEST_TBL,
                 'abac_test.v1 and IN (abac_test.v2, abac_test.v3)',
                 TEST_ROLE))

            # Should see nothing
            conn.assign_attribute('abac_test', 'v1', TEST_DB, TEST_TBL)
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 0)

            # Tag one of the columns with v2, it should be hidden now
            ctx.disable_auth()
            conn.assign_attribute('abac_test', 'v2', TEST_DB, TEST_TBL, 'col1')
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 1)

            # Tag the other column with the other tag, both should be visible
            ctx.disable_auth()
            conn.assign_attribute('abac_test', 'v3', TEST_DB, TEST_TBL, 'col2')
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 2)

            # Unassign one of the columns with v2, it should be hidden now
            ctx.disable_auth()
            conn.unassign_attribute('abac_test', 'v2', TEST_DB, TEST_TBL, 'col1')
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 1)

            # Unassign other columns with v1, it should be hidden now
            ctx.disable_auth()
            conn.unassign_attribute('abac_test', 'v3', TEST_DB, TEST_TBL, 'col2')
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 0)

    def test_das_3117(self):
        ctx = context()
        with ctx.connect() as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                # grant != pii at the view level
                conn.execute_ddl(
                    'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE(%s) TO ROLE %s' %\
                    (TEST_DB, ds, 'not abac_test.pii', TEST_ROLE))
                conn.assign_attribute('abac_test', 'pii', TEST_DB, ds)

                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0)

    def test_das_3119(self):
        ctx = context()
        with ctx.connect() as conn:
            ctx.disable_auth()
            self.__cleanup(conn)

            # Assign the attribute to a col on the table and view
            conn.assign_attribute('abac_test', 'pii', TEST_DB, TEST_TBL, 'col1')
            conn.assign_attribute('abac_test', 'pii', TEST_DB, TEST_VIEW, 'col1')

            conn.execute_ddl(
                'GRANT SELECT ON TABLE %s.%s HAS ATTRIBUTE(%s) TO ROLE %s' %\
                (TEST_DB, TEST_TBL, 'abac_test.pii', TEST_ROLE))
            conn.execute_ddl(
                'GRANT SELECT ON TABLE %s.%s HAS ATTRIBUTE(%s) TO ROLE %s' %\
                (TEST_DB, TEST_VIEW, 'abac_test.pii', TEST_ROLE))

            # User should have access to this column on both
            ctx.enable_token_auth(token_str=TEST_USER)

            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 1)
            self.__verify_tbl_access(conn, TEST_DB, TEST_VIEW, 1)

    def test_grant1(self):
        ctx = context()
        with ctx.connect() as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                conn.execute_ddl(
                    ('GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE ' +\
                    'abac_test.SALES AND NOT abac_test.PII TO ROLE %s') %\
                    (TEST_DB, ds, TEST_ROLE))

                # Should not have any access
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0)

                # Just assign sales
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'sales', TEST_DB, ds)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 3)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0, has_db_access=True)

                # Also assign PII, now should have no access
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'pii', TEST_DB, ds)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0)

    def test_grant2(self):
        ctx = context()
        with ctx.connect() as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                conn.execute_ddl(
                    ('GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE ' +\
                    'IN (abac_test.SALES, abac_test.MARKETING) ' +\
                    'AND NOT IN (abac_test.pii) TO ROLE %s') %\
                    (TEST_DB, TEST_ROLE))

                # Should not have any access
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0)

                # Assign sales to one and marketing to another, should have both
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'sales', TEST_DB, ds)
                conn.assign_attribute('abac_test', 'marketing', TEST_DB, TEST_TBL2)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 3)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 3)

                # Assign PII to one, now should not have access to that one
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'pii', TEST_DB, ds)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0, has_db_access=True)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 3)

                # Assign PII to the other, now should have no access
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'pii', TEST_DB, TEST_TBL2)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0, skip_metadata_check=True)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0,
                                         skip_metadata_check=True)

    def test_grant3(self):
        ctx = context()
        with ctx.connect() as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                conn.execute_ddl(
                    ('GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE ' +\
                    'IN (abac_test.SALES, abac_test.MARKETING) AND ' +\
                    'NOT abac_test.PII AND NOT abac_test.v1 TO ROLE %s') %\
                    (TEST_DB, TEST_ROLE))

                # Assign sales to one and marketing to another, should have both
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'sales', TEST_DB, ds)
                conn.assign_attribute('abac_test', 'marketing', TEST_DB, TEST_TBL2)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 3)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 3)

                # Assign PII to one and v1 to the other, should not have access
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'pii', TEST_DB, ds)
                conn.assign_attribute('abac_test', 'v1', TEST_DB, TEST_TBL2)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0, skip_metadata_check=True)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0,
                                         skip_metadata_check=True)

    def test_grant4(self):
        ctx = context()
        with ctx.connect() as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                conn.execute_ddl(
                    ('GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE ' +\
                    'IN (abac_test.SALES, abac_test.MARKETING) ' +\
                    'AND NOT IN(abac_test.PII, abac_test.v1) TO ROLE %s') % \
                    (TEST_DB, TEST_ROLE))

                # Assign sales to one and marketing to another, should have both
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'sales', TEST_DB, ds)
                conn.assign_attribute('abac_test', 'marketing', TEST_DB, TEST_TBL2)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 3)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 3)

                # Assign PII to one and v1 to the other, should not have access
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'pii', TEST_DB, ds)
                conn.assign_attribute('abac_test', 'v1', TEST_DB, TEST_TBL2)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 0,
                                         skip_metadata_check=True)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0,
                                         skip_metadata_check=True)

    def test_grant5(self):
        ctx = context()
        with ctx.connect() as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                conn.execute_ddl(
                    ('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
                    'IN (abac_test.SALES, abac_test.MARKETING) ' +\
                    'AND NOT IN(abac_test.PII, abac_test.v1) TO ROLE %s') % \
                    (TEST_ROLE))

                # Assign sales to one and marketing to another, should have both
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'sales', TEST_DB, ds)
                conn.assign_attribute('abac_test', 'marketing', TEST_DB, TEST_TBL2)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 3)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 3)

                # Assign PII to one and v1 to the other, should not have access
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'pii', TEST_DB, ds)
                conn.assign_attribute('abac_test', 'v1', TEST_DB, TEST_TBL2)
                ctx.enable_token_auth(token_str=TEST_USER)

                self.__verify_tbl_access(conn, TEST_DB, ds, 0,
                                         skip_metadata_check=True)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 0,
                                         skip_metadata_check=True)

    def test_grant7(self):
        grants = []
        grants.append(
            ('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
            '(NOT abac_test.PII OR NOT abac_test.email) TO ROLE %s') % \
            (TEST_ROLE))
        grants.append(
            ('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
            'NOT (abac_test.PII AND abac_test.email) TO ROLE %s') % \
            (TEST_ROLE))

        ctx = context()
        with ctx.connect() as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                for sql in grants:
                    ctx.disable_auth()
                    self.__cleanup(conn)

                    conn.execute_ddl(sql)

                    # Assign sales to one and marketing to another, should have both
                    conn.assign_attribute('abac_test', 'sales', TEST_DB, ds)
                    conn.assign_attribute('abac_test', 'pii', TEST_DB, ds, 'col1')
                    conn.assign_attribute('abac_test', 'pii', TEST_DB, ds, 'col2')
                    conn.assign_attribute('abac_test', 'email', TEST_DB, ds, 'col2')
                    conn.assign_attribute('abac_test', 'email', TEST_DB, ds, 'col3')

                    ctx.enable_token_auth(token_str=TEST_USER)
                    self.__verify_tbl_access(conn, TEST_DB, ds, 2)

    def test_grant6(self):
        # Regression test for DAS-2928
        ctx = context()
        with ctx.connect() as conn:
            for ds in [TEST_TBL]:
                ctx.disable_auth()
                self.__cleanup(conn)

                conn.execute_ddl(
                    ('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
                    'IN (abac_test.SALES, abac_test.MARKETING) ' +\
                    'AND NOT IN(abac_test.PII, abac_test.EMAIL) TO ROLE %s') % \
                    (TEST_ROLE))

                # Assign sales to the table
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'sales', TEST_DB, ds)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 3)

                # Assign PII to one and email to two different columns. These columns
                # should be hidden but the third column should be visible
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'pii', TEST_DB, ds, 'col1')
                conn.assign_attribute('abac_test', 'email', TEST_DB, ds, 'col2')
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, ds, 1)

    def test_das_3122(self):
        # grant attribute privileges for database to be removed
        ctx = context()
        with ctx.connect() as conn:
            ctx.disable_auth()
            self.__cleanup(conn)

            conn.assign_attribute('abac_test', 'v1', TEST_DB)
            self.__grant_abac_db(conn, TEST_DB, 'abac_test', 'v1')
            result = self.__show_grant_abac_role(conn)
            self.assertEqual(len(result), 1)

            # Drop and Ensure privilege is removed
            conn.execute_ddl("DROP DATABASE %s CASCADE INCLUDING PERMISSIONS " %\
                             TEST_DB)
            result = self.__show_grant_abac_role(conn)
            self.assertEqual(len(result), 0)

    def test_das_3122_tbl(self):
        ctx = context()
        with ctx.connect() as conn:
            for ds in [TEST_TBL, TEST_VIEW]:
                ctx.disable_auth()
                self.__cleanup(conn)

                TV = 'TABLE'
                if ds == TEST_VIEW:
                    TV = 'VIEW'

                # grant attribute privileges for table to be removed
                conn.assign_attribute('abac_test', 'v1', TEST_DB)
                self.__grant_abac_db(conn, TEST_DB, 'abac_test', 'v1')
                self.__grant_abac_tbl(conn, TEST_DB, ds, 'abac_test', 'v1')

                # Ensure privileges for db and table
                result = self.__show_grant_abac_role(conn)
                self.assertEqual(len(result), 2)
                self.assertTrue("database" in result[0][0])
                self.assertTrue("table" in result[1][0])

                conn.execute_ddl("DROP %s %s.%s INCLUDING PERMISSIONS" %\
                                 (TV, TEST_DB, ds))

                # Ensure privilege for DB only. Table privilege should have been dropped.
                result = self.__show_grant_abac_role(conn)
                self.assertEqual(len(result), 1)
                self.assertTrue("database" in result[0][0])

    def test_fixture1(self):
        ctx = context()
        with ctx.connect() as conn:
            ctx.disable_auth()
            self.__cleanup(conn, [TEST_DB, TEST_DB2])
            self.__fixture1(conn)

            # Grants that should all result in the same policies for these tests.
            grants = []
            grants.append(
                [('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
                'IN (abac_test.SALES) AND NOT IN(abac_test.PII) TO ROLE %s') % \
                (TEST_ROLE)])
            grants.append(
                [('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
                'IN (abac_test.SALES=true) AND NOT IN(abac_test.PII) TO ROLE %s') % \
                (TEST_ROLE)])
            grants.append(
                [('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
                'IN (abac_test.SALES!=false) AND NOT IN(abac_test.PII) TO ROLE %s') % \
                (TEST_ROLE)])
            grants.append(
                [('GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE ' +\
                'IN (abac_test.SALES) AND NOT IN(abac_test.PII) TO ROLE %s') % \
                (TEST_DB, TEST_ROLE),
                 ('GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE ' +\
                'IN (abac_test.SALES) AND NOT IN(abac_test.PII) TO ROLE %s') % \
                 (TEST_DB2, TEST_ROLE)])
            grants.append(
                [('GRANT SELECT ON DATABASE %s HAVING ATTRIBUTE ' +\
                'IN (abac_test.SALES) AND NOT IN(abac_test.PII) TO ROLE %s') % \
                (TEST_DB, TEST_ROLE),
                 ('GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE ' +\
                'IN (abac_test.SALES) AND NOT IN(abac_test.PII) TO ROLE %s') % \
                 (TEST_DB2, TEST_TBL, TEST_ROLE)])

            for grant in grants:
                for sql in grant:
                    conn.execute_ddl(sql)
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 2)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 2)
                self.__verify_tbl_access(conn, TEST_DB, TEST_VIEW, 2)
                self.__verify_tbl_access(conn, TEST_DB2, TEST_TBL, 2)
                self.__verify_tbl_access(conn, TEST_DB2, TEST_TBL2, 0, has_db_access=True)
                self.__verify_tbl_access(conn, TEST_DB2, TEST_VIEW, 0, has_db_access=True)

                ctx.disable_auth()
                for sql in grant:
                    self.__revoke(conn, sql)

            # Grant access to (sales and pii) or (marketing and v1)
            conn.execute_ddl(
                ('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
                'abac_test.SALES and abac_test.pii OR ' +\
                'abac_test.MARKETING and abac_test.v1 ' +\
                'TO ROLE %s') % (TEST_ROLE))
            ctx.enable_token_auth(token_str=TEST_USER)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 1)
            self.__verify_tbl_access(conn, TEST_DB, TEST_TBL2, 1)
            self.__verify_tbl_access(conn, TEST_DB, TEST_VIEW, 1)
            self.__verify_tbl_access(conn, TEST_DB2, TEST_TBL, 2)
            self.__verify_tbl_access(conn, TEST_DB2, TEST_TBL2, 1)
            self.__verify_tbl_access(conn, TEST_DB2, TEST_VIEW, 1)

    def test_white_list(self):
        # Test with a pii tag on the table and then white list on columns
        ctx = context()

        grants = []
        grants.append(
            ('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
            'abac_test.SALES and ' + \
            '(not abac_test.pii OR abac_test.v1 or abac_test.v2) ' +\
            'TO ROLE %s') % (TEST_ROLE))
        grants.append(
            ('GRANT SELECT ON CATALOG HAVING ATTRIBUTE ' +\
            'abac_test.SALES and ' + \
            'not (abac_test.pii and not abac_test.v1 and not abac_test.v2) ' +\
            'TO ROLE %s') % (TEST_ROLE))

        with ctx.connect() as conn:
            for sql in grants:
                ctx.disable_auth()
                self.__cleanup(conn, [TEST_DB, TEST_DB2])

                # Creates a representative test fixture. This will:
                # Tag TEST_DB with department sales
                # Tag TEST_DB.TEST_TBL with pii tags.
                conn.assign_attribute('abac_test', 'sales', TEST_DB)
                conn.assign_attribute('abac_test', 'pii', TEST_DB, TEST_TBL)

                # Issue the grant
                conn.execute_ddl(sql)

                ctx.enable_token_auth(token_str=TEST_USER)
                #self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 0, has_db_access=True)

                # Tag some of the columns with non-pii tags.
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'v1', TEST_DB, TEST_TBL, 'col1')
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 1)

                # Tag some of the columns with non-pii tags.
                ctx.disable_auth()
                conn.assign_attribute('abac_test', 'v2', TEST_DB, TEST_TBL, 'col2')
                conn.assign_attribute('abac_test', 'v1', TEST_DB, TEST_TBL, 'col3')
                conn.assign_attribute('abac_test', 'v2', TEST_DB, TEST_TBL, 'col3')
                ctx.enable_token_auth(token_str=TEST_USER)
                self.__verify_tbl_access(conn, TEST_DB, TEST_TBL, 3)

    def test_get_access_permissions(self):
        ctx = context()

        with ctx.connect() as conn:
            ctx.disable_auth()
            self.__cleanup(conn)

            conn.execute_ddl((
                'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE abac_test.v1 ' +
                'TO ROLE %s;') % (TEST_DB, TEST_TBL, TEST_ROLE))
            conn.execute_ddl((
                'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE ' +
                'abac_test.v2 TO ROLE %s;') % (TEST_DB, TEST_TBL2, TEST_ROLE))
            conn.execute_ddl((
                'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE ' +
                'abac_test.v3 TO ROLE %s;') % (TEST_DB, TEST_TBL2, TEST_ROLE))

            # Test that TEST_DB.TEST_TBL has expected attribute expressions
            params = _thrift_api.TGetAccessPermissionsParams()
            params.users_or_groups = []
            params.database = TEST_DB
            params.filter = TEST_TBL
            #pylint: disable=protected-access
            permissions = \
                conn._underlying_client().GetAccessPermissions(params).permissions
            #pylint: enable=protected-access
            test_role_permissions = [
                perm for perm in permissions
                if perm.database == TEST_DB and perm.table == TEST_TBL]
            self.assertEqual(len(test_role_permissions), 1)
            self.assertEqual(len(test_role_permissions[0].attribute_expression), 1)
            self.assertEqual(
                test_role_permissions[0].attribute_expression[0].__dict__,
                {
                    'role_name' : TEST_ROLE,
                    'expression' : 'abac_test.v1'})

            # Test that TEST_DB.TEST_TBL2 has expected attribute expressions
            params = _thrift_api.TGetAccessPermissionsParams()
            params.users_or_groups = []
            params.database = TEST_DB
            params.filter = TEST_TBL2
            #pylint: disable=protected-access
            permissions = \
                conn._underlying_client().GetAccessPermissions(params).permissions
            #pylint: enable=protected-access
            test_role_permissions = [
                perm for perm in permissions
                if perm.database == TEST_DB and perm.table == TEST_TBL2]
            self.assertEqual(len(test_role_permissions), 2)
            self.assertEqual(len(test_role_permissions[0].attribute_expression), 1)
            self.assertEqual(len(test_role_permissions[1].attribute_expression), 1)

            roles = [
                exp.role_name
                for exp in test_role_permissions[0].attribute_expression]
            roles = roles + [
                exp.role_name
                for exp in test_role_permissions[1].attribute_expression]
            expressions = [
                exp.expression for exp in test_role_permissions[0].attribute_expression]
            expressions = expressions + [
                exp.expression for exp in test_role_permissions[1].attribute_expression]

            self.assertEqual(set(roles), set([TEST_ROLE]))
            self.assertEqual(set(expressions), set(['abac_test.v2', 'abac_test.v3']))

    def test_drop_db(self):
        ctx = context()
        with ctx.connect() as conn:
            ctx.disable_auth()

            # Create our desired state of a single DB and table in it and a unique
            # role and user
            conn.execute_ddl("DROP TABLE IF EXISTS %s.%s" % (TEST_DB_DROP, TEST_TBL_DROP))
            conn.execute_ddl("DROP DATABASE IF EXISTS %s" % (TEST_DB_DROP))
            conn.execute_ddl("CREATE DATABASE %s" % (TEST_DB_DROP))
            conn.execute_ddl("CREATE TABLE %s.%s (i int)" % (TEST_DB_DROP, TEST_TBL_DROP))
            conn.execute_ddl("DROP ROLE IF EXISTS %s" % (TEST_ROLE_DROP))
            conn.execute_ddl("CREATE ROLE %s" % (TEST_ROLE_DROP))
            conn.execute_ddl("GRANT ROLE %s to GROUP %s"
                             % (TEST_ROLE_DROP, TEST_USER_DROP))

            conn.execute_ddl((
                'GRANT SELECT ON TABLE %s.%s HAVING ATTRIBUTE NOT IN (abac_test.v1) ' +
                'TO ROLE %s;') % (TEST_DB_DROP, TEST_TBL_DROP, TEST_ROLE_DROP))

            # Assign the tag to the table
            conn.assign_attribute('abac_test', 'pii', TEST_DB_DROP, TEST_TBL_DROP)

            # Ensure 'show databases' works for admin
            dbs = [db[0] for db in conn.execute_ddl('show databases')]
            self.assertTrue(TEST_DB_DROP in dbs)

            ctx.enable_token_auth(token_str=TEST_USER_DROP)

            # Ensure 'show databases' works for test user
            dbs = [db[0] for db in conn.execute_ddl('show databases')]
            self.assertTrue(TEST_DB_DROP in dbs)

            ctx.disable_auth()

            # Drop the DB and table
            conn.execute_ddl("DROP TABLE IF EXISTS %s.%s" % (TEST_DB_DROP, TEST_TBL_DROP))
            conn.execute_ddl("DROP DATABASE IF EXISTS %s" % (TEST_DB_DROP))

            ctx.enable_token_auth(token_str=TEST_USER_DROP)

            # Ensure 'show databases' works for test user (db shouldn't be there)
            dbs = [db[0] for db in conn.execute_ddl('show databases')]
            self.assertTrue(TEST_DB_DROP not in dbs)



if __name__ == "__main__":
    unittest.main()
