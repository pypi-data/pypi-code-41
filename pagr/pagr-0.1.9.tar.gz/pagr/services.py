from pathlib import Path
import importlib.util
import inspect
import os
from pagr.configuration import ConfigurationProvider


class ServiceLoader:
    def __init__(self, folder_path):
        self._instances = dict()

        self.folder_path = folder_path
        self.configuration = ConfigurationProvider()

        self.preload_folder_services()

    def preload_folder_services(self):
        module_name = os.path.basename(os.path.normpath(self.folder_path))
        abspath = os.path.abspath(self.folder_path)

        for pyfile in Path(os.path.join(abspath, 'services')).glob('**/*.py'):
            service_name = module_name + '.services.' + os.path.split(pyfile)[1].rsplit('.py')[0]

            spec = importlib.util.spec_from_file_location(service_name, pyfile)
            service = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(service)

            for name, obj in inspect.getmembers(service):
                if not inspect.isclass(obj):
                    continue
                if not name.endswith('Service'):
                    pass

                if name in self._instances:
                    raise Exception(f'Service {name} already exists')

                self._instances[name] = obj(self.configuration)

    def __getitem__(self, item):
        if item in self._instances:
            return self._instances[item]

    def __len__(self):
        return len(self._instances)
