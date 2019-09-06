"""
Databases and transactions should be created in a `with` statement
so that their context managers can safely release resources.
Keys and values are MessagePack-encoded bytes, returned as Python objects.
Keys are a tuple of UUID, timestamp, and attribute.
Copy the data if you want to keep it after the transaction.
Timestamps are in UTC format.

This is a thin wrapper around LMDB that extends those classes.
"""

import datetime
from uuid import uuid4

import lmdb
from msgpack import packb, unpackb


# Maximum number of tables that can exist (default 1 million).
MAX_TABLES = 1_000_000
# Maximum size of database in bytes (default 1 terabyte). 
MAX_SIZE = 1_000_000_000_000
# Storage format version the database is using
VERSION = 1

def uuid():
    """Generate a random unique ID."""
    return str(uuid4())

class SaviorException(Exception):
    """`SaviorException` represents any exception raised by this library."""
    pass

class Database():
    """
    Open the database at the given path with the given table names.
    The `tables` attribute on the returned object 
    is a dictionary of the tables within.
    """
    def __init__(self, path, table_names):
        self.path = path
        self.tables = {}
        self.env = lmdb.open(self.path, max_dbs=MAX_TABLES, map_size=MAX_SIZE)
        self.create_tables(table_names)

    def __enter__(self):
        return self

    def create_tables(self, table_names):
        """Create tables from a list of table names."""
        table_names.append('_metadata')
        # open the tables within the database
        with self.env.begin(write=True) as txn:
            for name in table_names:
                table = self.env.open_db(packb(name), txn=txn)
                self.tables[name] = table
            metadata = self.tables['_metadata']
            version = txn.get(b'version')
            if version == None:
                txn.put(packb('version'), packb(VERSION), db=self.tables['_metadata'])
        return self

    def __exit__(self, type, value, traceback):
        self.close()
        # don't suppress any errors
        return False

    def close(self):
        self.env.close()

    def begin(self, write=False):
        """Open a context managed transaction."""
        return Transaction(self, write=write)

    @property
    def VERSION(self):
        with self.env.begin() as txn:
            return unpackb(txn.get(packb('version'), db=self.tables['_metadata']))

def open(path, table_names=None):
    return Database(path, table_names=table_names)

class Transaction:
    def __init__(self, db, write=False):
        self.db = db
        self.write = write
        self.txn = self.db.env.begin(write=self.write)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        # Commit the transaction if there is no exception.
        if type == None:                           
            self.commit()                                     
        else:                
            self.abort()                                     
        # Don't suppress any exceptions.
        return False        

    def commit(self):
        self.txn.commit()                                     
        return self

    def abort(self):
        self.txn.abort()                                     
        return self

    def append_entry(self, table, uuid, attribute, value):
        """Low-level interface to append a single new entry."""
        now = datetime.datetime.utcnow().isoformat()
        key = (uuid, now, attribute)
        self.txn.put(packb(key), packb(value), db=self.db.tables[table])

    def store(self, table, attrs):
        """Store a new entity with the given attribtues and return its ID."""
        id = uuid()
        for attr, value in attrs.items():
            self.append_entry(table, id, attr, value)
        return id
    
    def fetch(self, table, uuid):
        """Get an entity with the given UUID in the given table."""
        entity = {}
        with self.txn.cursor(db=self.db.tables[table]) as cursor:
            key = (uuid, '', '')
            cursor.set_range(packb(key))
            # keys are sorted in ascending time order
            for key, value in cursor.iternext():
                next_id, time, attr = unpackb(key, use_list=False, raw=False)
                if next_id != uuid:
                    break
                entity[attr] = unpackb(value, raw=False)
        return entity
    
    def delete(self, table, uuid):
        """Delete an entity with the given UUID in the given table."""
        # key = (uuid, now, attribute)
        # self.txn.put(packb(key), packb(value), db=self.db.tables[table])
        keys = []
        with self.txn.cursor(db=self.db.tables[table]) as cursor:
            key = (uuid, '', '')
            cursor.set_range(packb(key))
            # keys are sorted in ascending time order
            for key, value in cursor.iternext():
                next_id, time, attr = unpackb(key, use_list=False, raw=False)
                if next_id != uuid:
                    break
                keys.append(key)
            for key in keys:
                self.txn.delete(key, db=self.db.tables[table])


    def update(self, table, uuid, attrs):
        """Update an entity with the given UUID and attributes."""
        for attr, value in attrs.items():
            self.append_entry(table, uuid, attr, value)
    
    def query(self, table, attrs, created_at=False):
        """
        Get all entities that have matching attribute-value entries.
        `attributes` is a dictionary of attributes that must match.
        Returns a dictionary of UUIDs to attribute-value dictionaries. 
        """
        entities = {}
        entity = {}
        current_id = None
        creation_date = None
        with self.txn.cursor(db=self.db.tables[table]) as cursor:
            # fetch each entity, and if attributes match, add it
            for key, value in cursor.iternext():
                uuid, time, attr = unpackb(key, use_list=False, raw=False)
                if current_id == None:
                    current_id = uuid
                    creation_date = time
                    if created_at:
                        entity['created_at'] = creation_date
                if current_id != uuid:
                    # check that attributes are subset of entity
                    if attrs.items() <= entity.items():
                        entities[current_id] = entity
                    # reset local variables
                    current_id = uuid
                    entity = {}
                    creation_date = time
                    # add the created_at date if requested
                    if created_at:
                        entity['created_at'] = creation_date
                entity[attr] = unpackb(value, raw=False)
            # add final entity if it matches
            if attrs.items() <= entity.items():
                entities[current_id] = entity
        return entities

