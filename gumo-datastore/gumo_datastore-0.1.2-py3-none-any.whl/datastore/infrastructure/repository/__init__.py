from contextlib import contextmanager

from gumo.core.injector import injector
from gumo.datastore.infrastructure.configuration import DatastoreConfiguration
from gumo.datastore.infrastructure.entity_key_mapper import EntityKeyMapper

from google.cloud import datastore


class DatastoreRepositoryMixin:
    _datastore_client = None
    _entity_key_mapper = None

    DatastoreEntity = datastore.Entity

    @property
    def datastore_client(self) -> datastore.Client:
        if self._datastore_client is None:
            configuration = injector.get(DatastoreConfiguration)  # type: DatastoreConfiguration
            self._datastore_client = configuration.client

        return self._datastore_client

    @property
    def entity_key_mapper(self) -> EntityKeyMapper:
        if self._entity_key_mapper is None:
            self._entity_key_mapper = injector.get(EntityKeyMapper)  # type: EntityKeyMapper

        return self._entity_key_mapper


@contextmanager
def datastore_transaction():
    datastore_client = injector.get(DatastoreConfiguration).client  # type: datastore.Client

    with datastore_client.transaction():
        yield
