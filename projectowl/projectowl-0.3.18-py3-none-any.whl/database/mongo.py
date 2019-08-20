"""MongoDB manager.
"""

import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId


def objectid_to_str(object_id):
  return str(object_id)


def str_to_objectid(id_str):
  return ObjectId(id_str)


class MongoDBManager(object):
  """MongoDB manager.
  """

  def __init__(self):
    self.client = None
    self.db = None

  def __del__(self):
    self.disconnect()

  def is_connected(self):
    """Check if connection is valid.
    """
    if self.client == None or \
    self.db == None:
      return False
    else:
      return True

  def connect(self,
              user=None,
              pwd=None,
              host=None,
              port=None,
              db_name=None,
              use_replica=False):
    """Connect to mongodb server.

    Args:
      user: user to login.
      pwd: pwd to login.
      host: server host.
      port: port to use.
      db_name: database to use.
      collection_name: collection to use.
    """
    if self.db is None:
      # make connection string.
      if host is None:
        db_url = "mongodb://127.0.0.1:27017"
      else:
        if not use_replica:
          db_url = "mongodb://{}:{}@{}:{}/{}".format(user, pwd, host, port,
                                                     db_name)
        else:
          db_url = "mongodb+srv://{}:{}@{}/{}".format(user, pwd, host, db_name)
      # get client.
      print("connecting to mongodb: {}".format(db_url))
      self.client = MongoClient(db_url)
      if db_name is not None:
        self.db = self.client[db_name]
        print("using db: {}".format(db_name))
      else:
        self.db = self.client["test"]
      print("mongodb connected")

  def delete_db(self, db_name):
    """Delete database.
    """
    self.client.drop_database(db_name)
    print("removed db: {}".format(db_name))

  def delete_collection(self, collection_name):
    """delete collection for current db.
    """
    collection = self.db[collection_name]
    collection.drop()
    print("current collection dropped.")

  def disconnect(self):
    """disconnect from server.
    """
    if self.client is not None:
      self.client.close()
      self.client = None
      self.db = None

  def create_index(self, collection_name, index_attribute):
    """Create index on current collection.

    Args:
      index_attribute: attribute name to index.
    """
    collection = self.db[collection_name]
    collection.create_index(index_attribute)
    print("index {} created.".format(index_attribute))

  def add_items(self, collection_name, items):
    """Add a new document.

    Args:
      items: documents to insert.
    Returns:
      number of documents inserted.
    """
    collection = self.db[collection_name]
    res = collection.insert_many(items)
    return len(res.inserted_ids)

  def get_items(self,
                collection_name,
                query,
                limit=0,
                offset=0,
                sort_key=None,
                sort_order=1):
    """Retrieve items given conditions.

    Args:
      sort_order: descending if 0, otherwise asecnding.
    """
    collection = self.db[collection_name]
    sort_order = pymongo.ASCENDING if sort_order == 1 else pymongo.DESCENDING
    if sort_key is None:
      items = list(collection.find(query, limit=limit, skip=offset))
    else:
      items = list(
          collection.find(
              query, limit=limit, skip=offset, sort=[(sort_key, sort_order)]))
    return items

  def count_items(self, collection_name, query):
    """Count item number.
    """
    collection = self.db[collection_name]
    num_items = collection.count_documents(query)
    return num_items

  def delete_items(self, collection_name, query):
    """Delete items based on query.

    Returns:
      number of deleted documents.
    """
    collection = self.db[collection_name]
    res = collection.delete_many(query)
    return res.deleted_count

  def update_items(self, collection_name, query, update_op):
    """Update items based on query.
    """
    collection = self.db[collection_name]
    collection.update_many(query, update_op)
