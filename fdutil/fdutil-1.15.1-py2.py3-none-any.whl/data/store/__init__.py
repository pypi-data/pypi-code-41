# encoding: utf-8

from ._constants import DATASTORE_ROOT_KEY

from .data_store import (set_global_datastore_persistence_store,
                         get_global_datastore_persistence_store,
                         setup_default_global_datastore_persistence_store,
                         DataStore)
