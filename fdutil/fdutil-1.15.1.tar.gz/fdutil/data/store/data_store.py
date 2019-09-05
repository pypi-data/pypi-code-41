# encoding: utf-8

from configurationutil import Configuration
from stateutil.persist import Persist, JSONPersistentStore
from . import DATASTORE_ROOT_KEY

global_datastore_persistence_store = None


def set_global_datastore_persistence_store(store):
    global global_datastore_persistence_store
    global_datastore_persistence_store = store
    return global_datastore_persistence_store


def get_global_datastore_persistence_store():
    global global_datastore_persistence_store
    if not global_datastore_persistence_store:
        raise ValueError(u'set_global_datastore_persistence_store has not been called.')
    return global_datastore_persistence_store


def setup_default_global_datastore_persistence_store():
    try:
        return get_global_datastore_persistence_store()

    except ValueError:
        store = JSONPersistentStore(root_folder=u'{d}/{r}'.format(d=Configuration().data_path_unversioned,
                                                                  r=DATASTORE_ROOT_KEY))
        return set_global_datastore_persistence_store(store)


class DataStore(Persist):

    def __init__(self,
                 key,
                 *args,
                 **kwargs):

        store = setup_default_global_datastore_persistence_store()

        super(DataStore, self).__init__(persistent_store=store,
                                        key=key,
                                        *args,
                                        **kwargs)
