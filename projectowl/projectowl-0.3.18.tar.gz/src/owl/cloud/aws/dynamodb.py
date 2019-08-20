"""OOP interface for DynamoDB.
"""

import boto3


class DynamoDBManager(object):
  """Class for managing dynamodb tasks.
  """

  def __init__(self, access_key, secret_key, region="us-east-1"):
    """Create dynamodb client.
    """
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region)
    self.resource = session.resource("dynamodb")

  def __get_table(self, table_name):
    """Retrieve table object.
    """
    return self.resource.Table(table_name)

  def get_table_item_count(self, table_name):
    """Get how many items are in the current table.
    """
    table = self.resource.Table(table_name)
    assert table.table_status == "ACTIVE", "table is not available"
    return table.item_count

  def create_table(self,
                   table_name,
                   partition_key,
                   sort_key=None,
                   read_cap=1,
                   write_cap=1):
    """Create a table.
    """
    # create one.
    key_schema = [{"AttributeName": partition_key, "KeyType": "HASH"}]
    attributes = [{"AttributeName": partition_key, "AttributeType": "S"}]
    if sort_key is not None:
      key_schema.append({"AttributeName": sort_key, "KeyType": "RANGE"})
      attributes.append({{"AttributeName": sort_key, "AttributeType": "S"}})
    table = self.resource.create_table(
        TableName=table_name,
        KeySchema=key_schema,
        # Only need to define keys type
        AttributeDefinitions=attributes,
        ProvisionedThroughput={
            "ReadCapacityUnits": read_cap,
            "WriteCapacityUnits": write_cap
        })
    print("table {} created.".format(table_name))

  def add_items(self, table_name, item):
    """Write attributes to current table.

    Args:
      item: name value pairs.
    """
    table = self.__get_table(table_name)
    with table.batch_writer() as batch:
      for cur_item in items:
        batch.put_item(Item=cur_item)

  def get_item(self, table_name, key_dict, attributes_to_get=None):
    """Get attributes from table.

    Args:
      key_dict: dictionary of primary key, e.g. {"id": ""}.
      attributes_to_get: projection expression to specify attributes.
    Returns:
      retrieved item with specified attributes.
    """
    table = self.__get_table(table_name)
    if attributes_to_get is None:
      res = table.get_item(Key=key_dict)
    else:
      res = table.get_item(Key=key_dict, AttributesToGet=attributes_to_get)
    if "Item" in res:
      return res["Item"]
    else:
      return None

  def scan_items(self, table_name, limit=10, cont_key=None):
    """Scan table and return items.

    Args:
      cont_key: key used to continue scan.
    Returns:
      current batch of items, continue_key (None if not exist).
    """
    table = self.__get_table(table_name)
    if cont_key is not None:
      response = table.scan(Limit=limit, ExclusiveStartKey=cont_key)
    else:
      response = table.scan(Limit=limit)
    cont_key = None
    if "LastEvaluatedKey" in response:
      cont_key = response["LastEvaluatedKey"]
    return response["Items"], cont_key

  def update_item(self, table_name, key_dict, attr_name, new_attr_val):
    """Update item value.

    Args:
      attr_name: name of attribute.
      new_attr_val: value for the attribut to set.

    Only support SET now.
    """
    table = self.__get_table(table_name)
    table.update_item(
        Key=key_dict,
        UpdateExpression="set {}=:newval".format(attr_name),
        ExpressionAttributeValues={":newval": new_attr_val})
