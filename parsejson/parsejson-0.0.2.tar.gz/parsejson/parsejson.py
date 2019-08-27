import os
import json
from dateutil.rrule import rrule


def parse_json_file(file_path, fields=None, **kwargs):
    '''Parse a Json file, Return: fields list
    :param file_path: where is json file
    :param fields: (optional) which fields will return with dict
    :param k=v ,...: (optional) which fields will return with kv
    
    Example: ::
        demo.json
            {"_id":1,"data":{"number":2}}
        >>> infos = parsejson.parse_json_file('demo.json', fields={'id':'_id', 'num':'data.number'})
        >>> print(infos)
        [{'id': 1, 'num': 2}]
        >>> infos = parsejson.parse_json_file('demo.json', id = '_id', num = 'data.number')
        >>> print(infos)
        [{'id': 1, 'num': 2}] 
    '''

    result = []
    fields = fields or kwargs
    
    if not fields:
        return result
    

    with open(file_path, 'r') as json_file:
        for json_line in json_file.readlines():
            json_data = json.loads(json_line)
            
            field_data = parse_filed(json_data, fields)
            print(field_data)
            result.append(field_data)
            
    return result


def parse_json_str(json_str, fields=None, **kwargs):
    '''Parse a Json string, Return: fields dict
    :param file_path: where is json file
    :param fields: (optional) which fields will return with dict
    :param k=v ,...: (optional) which fields will return with kv
    
    Example: ::
        >>> infos = parsejson.parse_json_str('{"_id":1,"data":{"number":2}}', fields={'id':'_id', 'num':'data.number'})
        >>> print(infos)
        [{'id': 1, 'num': 2}]
        >>> infos = parsejson.parse_json_str('{"_id":1,"data":{"number":2}}', id = '_id', num = 'data.number')
        >>> print(infos)
        {'id': 1, 'num': 2}
    '''
    
    result = []
    fields = fields or kwargs
    
    if not fields:
        return result 

    json_data = json.loads(json_str)
    field_data = parse_filed(json_data, fields)
    
    return field_data

    
def parse_filed(dict_data, fields):
    
    result = {}
    
    for name, field in fields.items():
        field_split = field.split('.')
        value = dict_data
        for k in field_split:
            try:
                value = value[k]
            except:
                value = None
                break
        result[name] = value
    
    return result