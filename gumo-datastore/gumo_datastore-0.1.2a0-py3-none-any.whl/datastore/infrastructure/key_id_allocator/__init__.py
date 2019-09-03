from typing import Optional
from typing import List
from injector import inject

from gumo.core.application.entity_key import KeyIDAllocator
from gumo.core.domain.entity_key import NoneKey
from gumo.core.domain.entity_key import EntityKey
from gumo.core.domain.entity_key import EntityKeyFactory
from gumo.core.domain.entity_key import IncompleteKey

from gumo.datastore.infrastructure.configuration import DatastoreConfiguration
from gumo.datastore.infrastructure import DatastoreRepositoryMixin

from google.cloud import datastore


class _IncompleteKeyMapper:
    @inject
    def __init__(
            self,
            datastore_configuration: DatastoreConfiguration,
            entity_key_factory: EntityKeyFactory,
    ):
        self._datastore_client = datastore_configuration.client
        self._entity_key_factory = entity_key_factory

    def to_datastore_key(self, incomplete_key: IncompleteKey) -> Optional[datastore.Key]:
        if incomplete_key is None or isinstance(incomplete_key, NoneKey):
            return None

        datastore_key = self._datastore_client.key(*incomplete_key.flat_pairs())

        return datastore_key

    def to_entity_key(self, datastore_key: Optional[datastore.Key]) -> EntityKey:
        if datastore_key is None:
            return NoneKey.get_instance()

        entity_key = self._entity_key_factory.build_from_pairs(pairs=datastore_key.path)
        return entity_key


class DatastoreKeyIDAllocator(KeyIDAllocator, DatastoreRepositoryMixin):
    ALLOCATE_BATCH_SIZE = 10

    @inject
    def __init__(
            self,
            key_mapper: _IncompleteKeyMapper,
    ):
        self.key_mapper = key_mapper

        self._cache = {}

    def _allocate_keys(
            self,
            incomplete_key: IncompleteKey,
            num_keys: int,
    ) -> List[EntityKey]:
        keys = self._cache.get(incomplete_key, [])

        if len(keys) < num_keys:
            if num_keys < self.ALLOCATE_BATCH_SIZE:
                allocate_nums = self.ALLOCATE_BATCH_SIZE
            else:
                allocate_nums = num_keys

            keys.extend(
                self._allocate_keys_without_cache(
                    incomplete_key=incomplete_key,
                    num_keys=allocate_nums
                )
            )

        allocated_keys = keys[0:num_keys]
        self._cache[incomplete_key] = keys[num_keys:]

        return allocated_keys

    def _allocate_keys_without_cache(
            self,
            incomplete_key: IncompleteKey,
            num_keys: int,
    ) -> List[EntityKey]:
        datastore_key = self.key_mapper.to_datastore_key(incomplete_key=incomplete_key)
        allocated_keys = self.datastore_client.allocate_ids(
            incomplete_key=datastore_key,
            num_ids=num_keys,
        )
        return [
            self.key_mapper.to_entity_key(datastore_key=key)
            for key in allocated_keys
        ]

    def allocate_keys(
            self,
            incomplete_key: IncompleteKey,
            num_keys: Optional[int] = None,
    ) -> List[EntityKey]:
        if num_keys is None:
            num_keys = self.ALLOCATE_BATCH_SIZE

        return self._allocate_keys(
            incomplete_key=incomplete_key,
            num_keys=num_keys,
        )

    def allocate(self, incomplete_key: IncompleteKey) -> EntityKey:
        return self.allocate_keys(
            incomplete_key=incomplete_key,
            num_keys=1,
        )[0]
