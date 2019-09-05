from psycopg2 import connect
from .collector import DirectoryCollector
from .versioner import SqlVersioner
from .migrator import Migrator


def sql_migrate(database_uri, migrations_path, schema='__template__',
                context={}, target_version='999999'):

    with connect(database_uri) as connection:
        migration_context = {
            'migrations_path': migrations_path,
            'connection': connection,
            'schema': schema
        }
        migration_context.update(context)

        collector = DirectoryCollector(migration_context)
        versioner = SqlVersioner(migration_context)
        migrator = Migrator(versioner, collector)

        migrator.migrate(target_version)
