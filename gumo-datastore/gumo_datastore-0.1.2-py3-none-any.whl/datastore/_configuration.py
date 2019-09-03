from logging import getLogger
from injector import singleton

from typing import Optional
from typing import Union

from gumo.core.injector import injector
from gumo.datastore.infrastructure.configuration import DatastoreConfiguration


logger = getLogger('gumo.datastore')


class ConfigurationFactory:
    @classmethod
    def build(
            cls,
            use_local_emulator: Union[str, bool, None] = None,
            emulator_host: Optional[str] = None,
            namespace: Optional[str] = None,
    ) -> DatastoreConfiguration:
        _use_emulator = False
        if isinstance(use_local_emulator, bool):
            _use_emulator = use_local_emulator
        elif isinstance(use_local_emulator, str):
            _use_emulator = use_local_emulator.lower() in ['true', 'yes']

        return DatastoreConfiguration(
            use_local_emulator=_use_emulator,
            emulator_host=emulator_host,
            namespace=namespace,
        )


def configure(
        use_local_emulator: Union[str, bool, None] = None,
        emulator_host: Optional[str] = None,
        namespace: Optional[str] = None,
) -> DatastoreConfiguration:
    config = ConfigurationFactory.build(
        use_local_emulator=use_local_emulator,
        emulator_host=emulator_host,
        namespace=namespace,
    )

    logger.debug(f'Gumo.Datastore is configured, config={config}')
    injector.binder.bind(DatastoreConfiguration, to=config, scope=singleton)

    from gumo.datastore._bind import datastore_binder
    injector.binder.install(datastore_binder)

    return config
