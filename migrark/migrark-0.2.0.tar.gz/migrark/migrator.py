from .versioner import Versioner
from .collector import Collector


class Migrator:

    def __init__(self, versioner: Versioner,  collector: Collector) -> None:
        self.versioner = versioner
        self.collector = collector

    def migrate(self, target='999999') -> None:
        migrations = self.collector.retrieve()
        version = self.versioner.version

        if target > version:
            for migration in migrations:
                if version < migration.version <= target:
                    migration.schema_up()
                    self.versioner.version = migration.version
        elif target < version:
            for migration in reversed(migrations):
                if target <= migration.version < version:
                    migration.schema_down()
                    self.versioner.version = migration.version
