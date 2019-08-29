#
#                __   _,--="=--,_   __
#               /  \."    .-.    "./  \
#              /  ,/  _   : :   _  \/` \
#              \  `| /o\  :_:  /o\ |\__/
#               `-'| :="~` _ `~"=: |
#                  \`     (_)     `/
#           .-"-.   \      |      /   .-"-.
#    .-----{     }--|  /,.-'-.,\  |--{     }-----.
#     )    (_)_)_)  \_/`~-===-~`\_/  (_(_(_)    (
#    (                                           )
#     )                Oriole-FAKE              (
#    (                  Eric.Zhou                )
#    '-------------------------------------------'
#

import mockredis
import mongomock
from oriole.vos import get_config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def fake_mongo():
    return mongomock.MongoClient().db.collection


def fake_redis():
    return mockredis.mock_redis_client()


class fake_db:
    def __init__(self, base='', uri='test_database'):
        self.base = base
        self.bind = create_engine(get_config().get(uri))
        self.base.metadata.create_all(self.bind)
        self.session = sessionmaker(self.bind)()

    def get(self):
        return self.session

    def close(self):
        self.session.rollback()
        self.session.close()
        self.base.metadata.drop_all(self.bind)
