"""
Create by yy on 2019-07-25
"""


class HelperTest(object):
    def __init__(self, init_db=None):
        self.db = init_db("INSOMNIA_MUSIC_DATABASE_CONFIG")

    def __del__(self):
        self.db.close()
