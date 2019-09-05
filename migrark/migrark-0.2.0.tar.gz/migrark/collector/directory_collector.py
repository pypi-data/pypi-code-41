from pathlib import Path
from typing import Dict, List, Any
from abc import ABC, abstractmethod
from importlib.util import spec_from_file_location, module_from_spec
from ..models import Migration
from .collector import Collector


class DirectoryCollector(Collector):
    def __init__(self, context: Dict[str, Any]) -> None:
        self.context = context
        self.path = self.context['migrations_path']

    def retrieve(self) -> List[Migration]:
        migrations = []
        for migration_file in Path(self.path).rglob('*.py'):
            migration = self._load_migration_file(migration_file)
            migrations.append(migration)

        return sorted(migrations, key=lambda m: m.version)

    def _load_migration_file(self, path: Path) -> Migration:
        spec = spec_from_file_location(path.stem, str(path))
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        return getattr(module, 'Migration')(self.context)
