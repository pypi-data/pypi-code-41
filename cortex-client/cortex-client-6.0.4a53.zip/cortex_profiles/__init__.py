# from cortex_profiles.internalprofilesclient import InternalProfilesClient
# from cortex_profiles.synthetic import create_profile_synthesizer
# from cortex_profiles.builders.attributes.implicit import ImplicitAttributesBuilder
# from cortex_profiles.builders.attributes.declared import DeclaredAttributesBuilder
# from cortex_profiles.schemas.dataframes import INTERACTIONS_COLS, INSIGHT_COLS, SESSIONS_COLS
#
#
# # # Test spinning up two python containers ...
# #     1. one that gets a lock and sleeps for 10 seconds
# #     2. another that waits unitl it gets a lock
# #
# #     The second one should wait until the first one finishes and releases the lock until it runs ...
#
#
# # def test_profile_locks():
# #     id = str(uuid.uuid4())
# #     print("lock p1", lock_profile("{}".format(id), "p1"))
# #     print("lock p2", lock_profile("{}".format(id), "p2"))
# #     print("lock p3", lock_profile("{}".format(id), "p3"))
# #     print("lock p1", lock_profile("{}".format(id), "p1"))
# #     print("lock p1", lock_profile("{}2".format(id), "p1"))
# #     print("lock p1", lock_profile("{}3".format(id), "p1"))
# #     print("lock p1", lock_profile("{}4".format(id), "p1"))
# #     print("lock p1", lock_profile("{}5".format(id), "p1"))
# #     print("lock p1", lock_profile("{}6".format(id), "p1"))
# #     print("unlock p1", unlock_profile("{}".format(id), "p1"))
# #     print("lock p1", lock_profile("{}7".format(id), "p1"))
#
# if __name__ == '__main__':
#     InternalProfilesClient.from_current_cli_profile()
#     synthesizer = create_profile_synthesizer()
