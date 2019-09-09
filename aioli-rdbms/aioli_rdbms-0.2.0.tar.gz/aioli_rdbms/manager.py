import databases

from sqlalchemy import create_engine


class DatabaseManager:
    url = None
    database: databases.Database = None
    engine = None
    configured = False

    @classmethod
    async def install(cls, config):
        if cls.configured:
            return

        cls.url = (
            f"{config['type']}://"
            f"{config['username']}:{config['password']}@"
            f"{config['host']}:{config['port']}/"
            f"{config['database']}"
        )

        cls.engine = create_engine(cls.url)
        cls.database = databases.Database(cls.url)

        await cls.database.connect()

        cls.configured = True

    @classmethod
    async def disconnect(cls):
        await cls.database.disconnect()
