#encoding: utf-8

""" File for loading data from Dynamo Tables """

from __future__ import print_function
from copy import deepcopy
from time import sleep
import boto3
from botocore.exceptions import ClientError

class Pynamo(object):
    """ Class for adding methods on top of boto3 dynamo client/session """

    def __init__(self, boto_session=None, table_prefix="", raise_exception=False, **kwargs):

        if boto_session:
            self.session = boto_session
        else:
            self.session = boto3.session.Session(**kwargs)
        self.client = self.session.client('dynamodb')
        self.raise_exception = raise_exception
        self.__table_prefix = table_prefix
        self.__default_response = {
            'status': 200,
            'error_msg': None,
            'data': []
        }

    def scan(self, table_name, **kwargs):
        """ Load in generic table """
        response = deepcopy(self.__default_response)
        kwargs['TableName'] = '%s%s' % (self.__table_prefix, table_name)
        while True:
            try:
                table_response = self.client.scan(**kwargs)
                response['data'].extend(self._dyno_dic(table_response.get('Items', [])))
                if not table_response.get('LastEvaluatedKey', None):
                    break
                else:
                    kwargs['ExclusiveStartKey'] = table_response['LastEvaluatedKey']
            except ClientError as error:
                return self.__return(self.__client_error(error, response, table_name))
        return self.__return(response)

    def get_item(self, table_name, key, **kwargs):
        """ Get Item from Dynamo Table """
        response = deepcopy(self.__default_response)
        kwargs['TableName'] = '%s%s' % (self.__table_prefix, table_name)
        kwargs['Key'] = self._dic_dyno(key)

        try:
            table_response = self.client.get_item(**kwargs)
        except ClientError as error:
            return self.__return(self.__client_error(error, response, table_name))

        response['data'] = self._dyno_dic([table_response.get('Item', None)])[0]
        if not response['data']:
            response['status'] = 404
            response['error_msg'] = "%s could not be found in %s." % (key, kwargs['TableName'])
        return self.__return(response)

    def put_item(self, table_name, item, overwrite=False, **kwargs):
        """ Put Item into Dynamo Table """
        response = deepcopy(self.__default_response)
        kwargs['TableName'] = '%s%s' % (self.__table_prefix, table_name)
        for key, value in item.items():
            if value == "":
                item[key] = None
        kwargs['Item'] = self._dic_dyno(item)

        # Check to make sure not overwriting same entry
        if not overwrite:

            # get table keys
            keys_response = self.table_keys(table_name)
            if keys_response['status'] != 200:
                return self.__return(keys_response)
            keys = keys_response['data']

            if keys["RANGE"]:
                condition = "NOT (attribute_exists(#name_hash) AND attribute_exists(#name_range))"
                expression_names = {"#name_hash": keys["HASH"], "#name_range": keys["RANGE"]}
            else:
                condition = "attribute_not_exists(#name_hash)"
                expression_names = {"#name_hash": keys["HASH"]}

            kwargs["ConditionExpression"] = condition
            kwargs["ExpressionAttributeNames"] = expression_names

        try:
            self.client.put_item(**kwargs)
        except ClientError as error:
            return self.__return(self.__client_error(error, response, table_name))
        response['data'] = item
        return self.__return(response)

    def delete_item(self, table_name, key, **kwargs):
        """ Delete Item from Dynamo Table """
        response = deepcopy(self.__default_response)
        kwargs['TableName'] = '%s%s' % (self.__table_prefix, table_name)
        kwargs['Key'] = self._dic_dyno(key)

        try:
            table_response = self.client.delete_item(**kwargs)
        except ClientError as error:
            return self.__return(self.__client_error(error, response, table_name))
        response['data'] = table_response
        return self.__return(response)

    def update_item(self, table_name, key, attribute_updates, **kwargs):
        """ Update Item in Dynamo Table """
        response = deepcopy(self.__default_response)
        kwargs['TableName'] = '%s%s' % (self.__table_prefix, table_name)
        kwargs['Key'] = self._dic_dyno(key)

        new_attributes = {}
        for up_key, up_value in attribute_updates.items():
            new_attributes[up_key] = {}
            new_attributes[up_key]['Action'] = up_value['Action']
            if 'Value' in up_value:
                new_attributes[up_key]['Value'] = self._dic_dyno(up_value['Value'], first=False)
        kwargs['AttributeUpdates'] = new_attributes

        try:
            table_response = self.client.update_item(**kwargs)
        except (ValueError, ClientError) as error:
            return self.__return(self.__client_error(error, response, table_name))
        response['data'] = table_response
        return self.__return(response)

    def replace_item(self, table_name, original_key, new_item):
        """ Rewrite Item to totally new item """
        response = deepcopy(self.__default_response)

        new_key = {key: value for (key, value) in new_item.items() if key in original_key.keys()}

        try:
            get_response = self.get_item(table_name, original_key)
            if get_response['status'] != 200:
                return self.__return(get_response)
        except (ValueError, ClientError) as error:
            return self.__return(self.__client_error(error, response, table_name))

        # Key not changed
        if new_key == original_key:
            return self.__return(self.put_item(table_name, new_item, overwrite=True))

        # Key changed
        put_table_response = self.put_item(table_name, new_item, overwrite=False)

        # Delete old entry
        if put_table_response['status'] == 200:
            del_table_response = self.delete_item(table_name, original_key)
            if del_table_response['status'] != 200:
                return self.__return(del_table_response)

        return self.__return(put_table_response)

    def table_keys(self, table_name):
        """ Get Table Hash and Range Keys """
        response = deepcopy(self.__default_response)
        try:
            describe_response = self.client.describe_table(TableName=table_name)['Table']
        except ClientError as error:
            return self.__return(self.__client_error(error, response, table_name))
        response['data'] = {
            "HASH": next((x["AttributeName"] for x in describe_response['KeySchema']
                          if x['KeyType'] == "HASH"), None),
            "RANGE": next((x["AttributeName"] for x in describe_response['KeySchema']
                           if x['KeyType'] == "RANGE"), None)
        }

        return self.__return(response)

    def table_keys_detailed(self, table_name):
        """ Get Table Hash and Range Keys as attributes with name and type """

        response = deepcopy(self.__default_response)
        try:
            describe_response = self.client.describe_table(TableName=table_name)['Table']
        except ClientError as error:
            return self.__return(self.__client_error(error, response, table_name))

        key_schema = describe_response["KeySchema"]
        attributes = describe_response["AttributeDefinitions"]

        hash_key_name = next((x["AttributeName"] for x in key_schema
                              if x['KeyType'] == "HASH"), None)
        range_key_name = next((x["AttributeName"] for x in key_schema
                               if x['KeyType'] == "RANGE"), None)

        response['data'] = {
            "HASH": next((x for x in attributes if x["AttributeName"] == hash_key_name), None),
            "RANGE": next((x for x in attributes if x["AttributeName"] == range_key_name), None)
        }

        return self.__return(response)


    def table_key_values(self, table_name):
        """ Scan that only returns key values """

        # get table keys
        keys_response = self.table_keys(table_name)
        if keys_response['status'] != 200:
            return self.__return(keys_response)
        keys = keys_response['data']

        response = self.scan(table_name, AttributesToGet=[x for x in keys.values() if x])
        return self.__return(response)

    def copy_table(self, source_table, target_table, data_update=None,
                   source_profile=None, target_profile=None, clear_table=False):
        """ Copy Table to another existing Table """

        response = deepcopy(self.__default_response)

        # Define clients
        old_client = self.client
        try:
            source_client = boto3.session.Session(
                profile_name=source_profile).client('dynamodb') if source_profile else self.client
            target_client = boto3.session.Session(
                profile_name=target_profile).client('dynamodb') if target_profile else self.client
        except Exception as error:
            response['status'] = 403
            response['error_msg'] = str(error)
            return self.__return(response)

        try:
            # Source
            self.client = source_client
            source_data = self.scan(source_table)['data']

        except ClientError as error:
            self.client = old_client
            return self.__return(self.__client_error(error, response, table_name=source_table))
        except Exception as error:
            self.client = old_client
            return self.__return(self.__default_error(error, response))

        ## data_update
        if data_update:
            for data in source_data:
                data.update(data_update)

        try:
            # Target
            self.client = target_client
            if clear_table:
                delete_keys = self.table_key_values(target_table)['data']
                delete_requests = [{'DeleteRequest': {'Key': self._dic_dyno(key)}} for key in delete_keys]
                self.__batch_write(target_table, delete_requests)

            # Source table
            put_requests = [{'PutRequest': {'Item': self._dic_dyno(item)}} for item in source_data]
            self.__batch_write(target_table, put_requests)

        except ClientError as error:
            self.client = old_client
            return self.__return(self.__client_error(error, response, table_name=target_table))
        except Exception as error:
            self.client = old_client
            return self.__return(self.__default_error(error, response))

        self.client = old_client
        return response

    def __batch_write(self, table_name, requests, chunk_size=15):
        requests_split = [requests[i:i + chunk_size]
                          for i in range(0, len(requests), chunk_size)]
        for request_list in requests_split:
            sleep_time = 0
            request_items = {table_name: request_list}
            while request_items.keys():
                sleep(sleep_time)
                request_items = self.client.batch_write_item(RequestItems=request_items).get("UnprocessedItems", [])
                sleep_time = 2 * (sleep_time + 1)
                if request_items.keys():
                    print("%s items unprocessed.  Sleeping for %s seconds..." % (len(request_items.get(table_name, [])), sleep_time))


    def __return(self, response):
        if self.raise_exception and response['status'] != 200:
            raise Exception(response['error_msg'])
        return response



####################################################################################################

    def convert_key(self, table_name, key):
        """ convert key to correct type for table """
        response = deepcopy(self.__default_response)

        table_keys_response = self.table_keys_detailed(table_name)
        if table_keys_response['status'] != 200:
            return table_keys_response
        
        table_keys = table_keys_response['data']
        key_transform = {"N": float, "S": str}

        hash_key_name = table_keys["HASH"]["AttributeName"]
        hash_key_transform = key_transform[table_keys["HASH"]["AttributeType"]]

        if hash_key_name not in key.keys():
            response["status"] = 404
            response["error_msg"] = "Missing Hash Key: %s" % hash_key_name
            return response

        final_key = {
            hash_key_name: hash_key_transform(key[hash_key_name])
        }

        if table_keys.get("RANGE", None):
            range_key_name = table_keys["RANGE"]["AttributeName"]
            range_key_transform = key_transform[table_keys["RANGE"]["AttributeType"]]
            if range_key_name not in key.keys():
                response["status"] = 404
                response["error_msg"] = "Missing Range Key: %s" % range_key_name
                return response
            final_key[range_key_name] = range_key_transform(key[range_key_name])

        response['data'] = final_key
        return response


    def _dyno_dic(self, dyna_data, data_type=None, first=True):
        """ Convert dynamodb reponse to standard dictionary """
        data_keys = {
            "BOOL": bool,
            "N": float,
            "B": str
        }

        if first:
            return [self._dyno_dic(x, data_type=None, first=False) for x in dyna_data]
        elif data_type == "NULL" or dyna_data is None:
            return None
        elif isinstance(dyna_data, dict):
            return {str(k): self._dyno_dic(v[list(v.keys())[0]], data_type=list(v.keys())[0], first=False)
                    for (k, v) in dyna_data.items()}
        elif isinstance(dyna_data, list) and data_type != "SS" and data_type != "NS":
            return [self._dyno_dic(x[list(x.keys())[0]], data_type=list(x.keys())[0], first=False)
                    for x in dyna_data]
        elif data_type in data_keys:
            return data_keys[data_type](dyna_data)
        return dyna_data

    def _dic_dyno(self, input_value, first=True):
        """ Convert standard dictionary to dynamodb """
        type_keys = {
            int: "N",
            float: "N"
        }

        if first:
            return {str(k): self._dic_dyno(v, first=False) for (k, v) in input_value.items()}
        if isinstance(input_value, dict):
            return {"M": {k: self._dic_dyno(v, first=False) for (k, v) in input_value.items()}}
        elif isinstance(input_value, list):
            return {"L": [self._dic_dyno(x, first=False) for x in input_value]}
        elif input_value is None or input_value == "":
            return {"NULL": True}
        elif isinstance(input_value, bool):
            return {"BOOL": input_value}
        elif type(input_value) in type_keys:
            return {type_keys[type(input_value)]: str(input_value)}
        return {"S": input_value}


    def __client_error(self, error, response, table_name=None):
        if "response" not in dir(error):
            response['status'] = 500
            response['error_msg'] = str(error)
        elif error.response['Error']['Code'] == 'ResourceNotFoundException':
            response['status'] = 404
            response['error_msg'] = "%s could not be found." % str(table_name)
        elif error.response['Error']['Code'] == 'ExpiredTokenException':
            response['status'] = 403
            response['error_msg'] = "Token expired"
        elif error.response['Error']['Code'] in ['ConditionalCheckFailedException', 'ValidationException', 'UnrecognizedClientException']:
            response['status'] = 403
            response['error_msg'] = str(error)
        else:
            response['status'] = 500
            response['error_msg'] = str(error)
        return response

    def __default_error(self, error, response):
        response['status'] = 500
        response['error_msg'] = str(error)
        return response
