# Copyright 2019 Okera Inc. All Rights Reserved.
#
# Some integration tests for role granting
#
# pylint: disable=too-many-arguments
# pylint: disable=too-many-public-methods

import unittest

from okera import context, _thrift_api

TEST_USER = 'roles_test_user'

def disable_auth(ctx, params):
    ctx.disable_auth()
    params.requesting_user = None

def enable_auth(ctx, params, user):
    ctx.enable_token_auth(token_str=user)
    params.requesting_user = user

def get_grantable_roles(conn, params):
    #pylint: disable=protected-access
    return conn._underlying_client().GetGrantableRoles(params)
    #pylint: enable=protected-access

class RolesTest(unittest.TestCase):
    # NOTE: this test will likely need to change once we can properly
    # ACL roles themselves, since then we will return just a subset of
    # roles.
    def test_get_grantable_roles(self):
        ctx = context()
        with ctx.connect() as conn:
            params = _thrift_api.TGetGrantableRolesParams()

            # Set up a role and grant it to the user's group
            disable_auth(ctx, params)
            conn.execute_ddl("DROP ROLE IF EXISTS grantable_role")
            conn.execute_ddl("CREATE ROLE grantable_role")
            conn.execute_ddl("GRANT ROLE grantable_role to GROUP %s" % TEST_USER)

            # As an admin, we should always be able to see all roles
            disable_auth(ctx, params)
            response = get_grantable_roles(conn, params)
            retrieved_roles = response.roles
            self.assertTrue(len(retrieved_roles) > 0)
            self.assertTrue("grantable_role" in retrieved_roles)

            # Even though we have the test role, our user does not have
            # any roles that have a privilege with GRANT OPTION, so we
            # should not get back any roles
            enable_auth(ctx, params, TEST_USER)
            response = get_grantable_roles(conn, params)
            retrieved_roles = response.roles
            self.assertTrue(len(retrieved_roles) == 0)

            # As an admin, grant a privilege with GRANT OPTION to the
            # role we created
            disable_auth(ctx, params)
            conn.execute_ddl("""
            GRANT SELECT ON TABLE okera_sample.sample
            TO ROLE grantable_role WITH GRANT OPTION""")
            admin_roles = get_grantable_roles(conn, params).roles

            # Even though there is a grant with GRANT OPTION, it's on
            # a specific table, and we specify no parameters, which is
            # equivalent to searching for grants on the CATALOG
            enable_auth(ctx, params, TEST_USER)
            response = get_grantable_roles(conn, params)
            retrieved_roles = response.roles
            self.assertTrue(len(retrieved_roles) == 0)

            # Now, we will check with specific parameters
            params.database = "okera_sample"
            params.table = "sample"

            # As a user, we should now get back all the roles since we have a
            # privilege that has a GRANT OPTION that matches our scope. The set of
            # roles should be the same as what the admin got.
            enable_auth(ctx, params, TEST_USER)
            response = get_grantable_roles(conn, params)
            retrieved_roles = response.roles
            self.assertTrue(len(retrieved_roles) > 0)
            self.assertEqual(admin_roles, retrieved_roles)

            # Now, we will check with specific parameters on a table we don't have
            params.database = "okera_sample"
            params.table = "users"

            # As a user, we should get no roles, as we don't have a GRANT OPTION
            # on that specific scope
            enable_auth(ctx, params, TEST_USER)
            response = get_grantable_roles(conn, params)
            retrieved_roles = response.roles
            self.assertTrue(len(retrieved_roles) == 0)

            # Now, we will check with specific parameters on just the DB
            params.database = "okera_sample"

            # As a user, we should get no roles, as we don't have a GRANT OPTION
            # on that specific scope
            enable_auth(ctx, params, TEST_USER)
            response = get_grantable_roles(conn, params)
            retrieved_roles = response.roles
            self.assertTrue(len(retrieved_roles) == 0)

            # As an admin, grant a privilege with GRANT OPTION to the
            # role we created
            disable_auth(ctx, params)
            conn.execute_ddl("""
            GRANT SELECT ON DATABASE okera_sample
            TO ROLE grantable_role WITH GRANT OPTION""")

            # As a user, we should now get all roles, as we have a GRANT OPTION
            # on that specific scope
            enable_auth(ctx, params, TEST_USER)
            response = get_grantable_roles(conn, params)
            retrieved_roles = response.roles
            self.assertTrue(len(retrieved_roles) > 0)
            self.assertEqual(admin_roles, retrieved_roles)

            # Now, we will check with specific parameters on just the DB,
            # with a different DB
            params.database = "okera_system"

            # As a user, we should get no roles, as we don't have a GRANT OPTION
            # on that specific scope
            enable_auth(ctx, params, TEST_USER)
            response = get_grantable_roles(conn, params)
            retrieved_roles = response.roles
            self.assertTrue(len(retrieved_roles) == 0)

            # Finally, let's add a grant to the CATALOG and then
            # a query with no parameters will work
            disable_auth(ctx, params)
            conn.execute_ddl("""
            GRANT SELECT ON SERVER
            TO ROLE grantable_role WITH GRANT OPTION""")

            # Now, we will check with no parameters
            params.database = ""
            params.table = ""

            # As a user, we should get all the roles, we have GRANT OPTION
            # at the CATALOG level
            enable_auth(ctx, params, TEST_USER)
            response = get_grantable_roles(conn, params)
            retrieved_roles = response.roles
            self.assertTrue(len(retrieved_roles) > 0)
            self.assertEqual(admin_roles, retrieved_roles)

            # Additionally, even if we query on a specific DB (or even table),
            # we will now always get roles because our CATALOG level grant
            # allows us to see them.
            params.database = "okera_system"

            enable_auth(ctx, params, TEST_USER)
            response = get_grantable_roles(conn, params)
            retrieved_roles = response.roles
            self.assertTrue(len(retrieved_roles) > 0)
            self.assertEqual(admin_roles, retrieved_roles)

if __name__ == "__main__":
    unittest.main()
