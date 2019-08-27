# Copyright 2019 Okera Inc. All Rights Reserved.
#
# Some integration tests for managing attributes
#
# pylint: disable=too-many-arguments

import unittest

from okera import context

class AttributesTest(unittest.TestCase):
    @staticmethod
    def _contains_attribute(namespace, key, attributes):
        for attr in attributes:
            if attr.attribute_namespace == namespace and attr.key == key:
                return True
        return False

    @staticmethod
    def _collect_column_attributes(ds):
        result = {}
        for col in ds.schema.cols:
            if not col.attribute_values:
                continue
            for v in col.attribute_values:
                key = v.database
                if v.table:
                    key += '.' + v.table
                    if v.column:
                        key += '.' + v.column
                if key not in result:
                    result[key] = []
                result[key].append(v)
        return result

    def _verify_attr(self, val, namespace, key, db, tbl, col):
        self.assertTrue(val.attribute.attribute_namespace == namespace)
        self.assertTrue(val.attribute.key == key)
        self.assertTrue(val.database == db)
        self.assertTrue(val.table == tbl)
        self.assertTrue(val.column == col)

    def test_basic(self):
        with context().connect() as conn:
            conn.create_attribute('abac_test', 'v1', True)
            conn.create_attribute('abac_test', 'v2', True)
            attributes = conn.list_attributes('abac_test')
            self.assertTrue(len(attributes) >= 2, msg=str(attributes))
            self.assertTrue(self._contains_attribute('abac_test', 'v1', attributes),
                            msg=str(attributes))
            self.assertTrue(self._contains_attribute('abac_test', 'v2', attributes),
                            msg=str(attributes))
            old_len = len(attributes)
            namespaces = conn.list_attribute_namespaces()
            self.assertTrue('abac_test' in namespaces)

            # Delete the attribute and make sure it is gone
            self.assertTrue(conn.delete_attribute('abac_test', 'v2'))
            attributes = conn.list_attributes('abac_test')
            self.assertTrue(old_len == len(attributes) + 1)
            self.assertTrue(self._contains_attribute('abac_test', 'v1', attributes),
                            msg=str(attributes))
            self.assertFalse(self._contains_attribute('abac_test', 'v2', attributes),
                             msg=str(attributes))
            namespaces = conn.list_attribute_namespaces()
            self.assertTrue('abac_test' in namespaces)

    def test_multiple_namespaces(self):
        with context().connect() as conn:
            conn.create_attribute('abac_test1', 'v', True)
            conn.create_attribute('abac_test2', 'v', True)
            conn.create_attribute('abac_test3', 'v', True)

            namespaces = conn.list_attribute_namespaces()
            self.assertTrue('abac_test1' in namespaces)
            self.assertTrue('abac_test2' in namespaces)
            self.assertTrue('abac_test3' in namespaces)

            attributes = conn.list_attributes('abac_test1')
            self.assertTrue(self._contains_attribute('abac_test1', 'v', attributes))
            self.assertFalse(self._contains_attribute('abac_test2', 'v', attributes))

            # List in all namespaces
            attributes = conn.list_attributes()
            self.assertTrue(self._contains_attribute('abac_test1', 'v', attributes))
            self.assertTrue(self._contains_attribute('abac_test2', 'v', attributes))
            self.assertTrue(self._contains_attribute('abac_test3', 'v', attributes))

            attributes = conn.list_attributes(None)
            self.assertTrue(self._contains_attribute('abac_test1', 'v', attributes))
            self.assertTrue(self._contains_attribute('abac_test2', 'v', attributes))
            self.assertTrue(self._contains_attribute('abac_test3', 'v', attributes))

            attributes = conn.list_attributes('')
            self.assertTrue(self._contains_attribute('abac_test1', 'v', attributes))
            self.assertTrue(self._contains_attribute('abac_test2', 'v', attributes))
            self.assertTrue(self._contains_attribute('abac_test3', 'v', attributes))

    def test_create_delete(self):
        with context().connect() as conn:
            conn.delete_attribute('abac_test', 'v1')
            conn.delete_attribute('abac_test', 'v2')

            # Try deleting again, should not exist
            self.assertFalse(conn.delete_attribute('abac_test', 'v1'))
            self.assertFalse(conn.delete_attribute('abac_test', 'v2'))

            # Try creating, should not need to specify if exists
            conn.create_attribute('abac_test', 'v1', False)
            conn.create_attribute('abac_test', 'v2', False)
            attributes = conn.list_attributes('abac_test')
            self.assertTrue(len(attributes) >= 2, msg=str(attributes))
            self.assertTrue(self._contains_attribute('abac_test', 'v1', attributes),
                            msg=str(attributes))
            self.assertTrue(self._contains_attribute('abac_test', 'v2', attributes),
                            msg=str(attributes))

            # Try creating without if exists, should fail
            with self.assertRaises(RuntimeError) as ex_ctx:
                conn.create_attribute('abac_test', 'v1', False)
            self.assertTrue('already exists' in str(ex_ctx.exception))

            with self.assertRaises(RuntimeError) as ex_ctx:
                conn.create_attribute('abaC_test', 'v1', False)
            self.assertTrue('already exists' in str(ex_ctx.exception))

            with self.assertRaises(RuntimeError) as ex_ctx:
                conn.create_attribute('ABAC_TEST', 'V1', False)
            self.assertTrue('already exists' in str(ex_ctx.exception))

            with self.assertRaises(RuntimeError) as ex_ctx:
                conn.create_attribute('abac_test', 'v2', False)
            self.assertTrue('already exists' in str(ex_ctx.exception))

            # Try deleting should exist
            self.assertTrue(conn.delete_attribute('abac_test', 'v1'))
            self.assertTrue(conn.delete_attribute('ABAC_test', 'V2'))

    def test_assign_get_attributes(self):
        db = 'attributes_test_db'
        with context().connect() as conn:
            conn.create_attribute('abac_test', 'V1', True)
            conn.create_attribute('ABAC_test', 'v2', True)

            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db)
            conn.execute_ddl('CREATE DATABASE %s' % db)
            self.assertTrue(len(conn.list_datasets(db)) == 0)

            # Create 2 tables and 2 views
            conn.execute_ddl('CREATE TABLE %s.t1(c1 int, c2 int, c3 int)' % db)
            conn.execute_ddl('CREATE TABLE %s.t2(c1 int, c2 int, c3 int)' % db)
            conn.execute_ddl('CREATE VIEW %s.v1 AS SELECT * from %s.t1' % (db, db))
            conn.execute_ddl('CREATE VIEW %s.v2 AS SELECT * from %s.t1' % (db, db))
            self.assertTrue(len(conn.list_datasets(db)) == 4)

            # Get the attributes on t1, should be empty
            ds = conn.list_datasets(db, name='t1')[0]
            self.assertTrue(ds.attribute_values is None)
            attrs_by_col = self._collect_column_attributes(ds)
            self.assertTrue(not attrs_by_col)

            # Assign abac_test.v1 to t1
            conn.assign_attribute('abac_TEST', 'v1', db, 't1')
            # TODO: this assign doesn't fail cleanly. The planner fails the request
            # but when the attributes are received, there are duplicates. Fix this
            # in the planner.
            # conn.assign_attribute('abac_test', 'v1', db, 't1', if_not_exists=True)
            ds = conn.list_datasets(db, name='t1')[0]
            attrs = ds.attribute_values
            self.assertTrue(attrs is not None)
            self.assertTrue(len(attrs) == 1)
            self._verify_attr(attrs[0], 'abac_test', 'v1', db, 't1', None)
            self.assertTrue(not self._collect_column_attributes(ds))

            # Assign abac_test.v2 to t1
            conn.assign_attribute('abac_test', 'v2', db, 't1')
            ds = conn.list_datasets(db, name='t1')[0]
            attrs = ds.attribute_values
            self.assertTrue(attrs is not None)
            self.assertTrue(len(attrs) == 2)
            if attrs[0].attribute.key == 'v1':
                self._verify_attr(attrs[0], 'abac_test', 'v1', db, 't1', None)
                self._verify_attr(attrs[1], 'abac_test', 'v2', db, 't1', None)
            else:
                self._verify_attr(attrs[1], 'abac_test', 'v1', db, 't1', None)
                self._verify_attr(attrs[0], 'abac_test', 'v2', db, 't1', None)

            # Assign abac_test.v1 to v1 and v2.c2
            conn.assign_attribute('abac_test', 'v1', db, 'v1')
            conn.assign_attribute('abac_test', 'v1', db, 'v2', 'c2')
            ds = conn.list_datasets(db, name='v1')[0]
            self._verify_attr(ds.attribute_values[0], 'abac_test', 'v1', db, 'v1', None)

            ds = conn.list_datasets(db, name='v2')[0]
            self.assertTrue(ds.attribute_values is None)
            attrs = self._collect_column_attributes(ds)
            self.assertTrue(('%s.v2.c2' % db) in attrs)
            self.assertTrue(('%s.v2.c1' % db) not in attrs)

            # Try again with upper case db
            ds = conn.list_datasets(db.upper(), name='V2')[0]
            self.assertTrue(ds.attribute_values is None)
            attrs = self._collect_column_attributes(ds)
            self.assertTrue(('%s.v2.c2' % db) in attrs)
            self.assertTrue(('%s.v2.c1' % db) not in attrs)

            # Unassign abac_test.v1 from v2.c2
            conn.unassign_attribute('ABAC_test', 'v1', db, 'v2', 'c2')
            ds = conn.list_datasets(db, name='v2')[0]
            self.assertTrue(ds.attribute_values is None)
            attrs = self._collect_column_attributes(ds)
            self.assertTrue(not attrs)
            # Verify the assignment to v1 is still there
            ds = conn.list_datasets(db, name='v1')[0]
            self._verify_attr(ds.attribute_values[0], 'abac_test', 'v1', db, 'v1', None)

            # Unassign abac_test.v1 from v1
            conn.unassign_attribute('abac_test', 'V1', db, 'v1')
            ds = conn.list_datasets(db, name='v1')[0]
            self.assertTrue(ds.attribute_values is None)

    def test_assign_invalid_attributes(self):
        db = 'attributes_test_db'
        with context().connect() as conn:
            conn.create_attribute('abac_test', 'V1', True)

            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db)
            conn.execute_ddl('CREATE DATABASE %s' % db)

            conn.assign_attribute('abac_test', 'v1', db)
            with self.assertRaises(Exception) as ex_ctx:
                conn.assign_attribute('abac_test', 'not-there', db)
            self.assertTrue('Cannot assign attributes' in str(ex_ctx.exception),
                            msg=str(ex_ctx.exception))

if __name__ == "__main__":
    unittest.main()
