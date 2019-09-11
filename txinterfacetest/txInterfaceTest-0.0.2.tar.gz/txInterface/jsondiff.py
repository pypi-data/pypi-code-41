#!/usr/bin/python
#_*_encoding:utf-8_*_

import json
from basic import logger
def readFile(filename):
    content = ''
    f = open(filename)
    for line in f:
        content += line.strip("\n")
    f.close()
    return content

def parseKeys(jsonobj):
    jsonkeys = list()
    jsonAll= list()
    addJsonKeys(jsonobj, jsonkeys,jsonAll, '')
    return jsonkeys

def jsonAll(jsonobj):
    jsonkeys = list()
    jsonAll= list()
    addJsonKeys(jsonobj, jsonkeys,jsonAll, '')
    return jsonAll


def addJsonKeys(jsonobj, keys,jsonAll, prefix_key):
    if prefix_key != '':
        prefix_key = prefix_key+'.'
    if isinstance(jsonobj, list):
        addKeysIflist(jsonobj, keys,jsonAll, prefix_key)
    elif isinstance(jsonobj, dict):
        addKeysIfdict(jsonobj, keys,jsonAll, prefix_key)

def addKeysIflist(jsonlist, keys,jsonAll, prefix_key):
    if len(jsonlist) > 0:
        for i in range(len(jsonlist)) :
            addJsonKeys(jsonlist[i], keys,jsonAll, prefix_key)

def addKeysIfdict(jsonobj, keys,jsonAll, prefix_key):
    for (key, value) in jsonobj.iteritems():
        result = compare((prefix_key + key), keys)
        if 0 == result:
            keys.append(prefix_key + key)
            jsonAll.append((prefix_key + key)+"."+str(value))
        else:
            keys.append(prefix_key + key+str(result))
            jsonAll.append((prefix_key + key+str(result))+"."+str(value))
        addJsonKeys(value, keys,jsonAll, prefix_key+key)

def compare(key, keys):
    count = 0
    for param in keys:
        if key in param:
            test = key.split(".")
            if test[test.__len__()-1].isdigit() is True :
                continue
            result = param.replace(key, "")
            if str(result).isdigit() is True or "" == result:
                count = count + 1
    return count

def diffKeys(json1, json2,flag):
    keys1=""
    keys2=""
    if 1 == flag:
        keys1 = parseKeys(json1)
        keys2 = parseKeys(json2)
    elif 2 == flag:
        keys1 = jsonAll(json1)
        keys2 = jsonAll(json2)
    logger.info("The current JSON is  " + str(keys1))
    logger.info("The target JSON is  " + str(keys2))
    keyset1 = set(keys1)
    keyset2 = set(keys2)
    return keyset1.difference(keyset2)



if __name__ == "__main__":

    content = readFile('json_data.txt')
    jsondataArr = content.split(';;;')
    content1 = jsondataArr[0]
    content2 = jsondataArr[1]
    json1 = json.loads(content1)
    json2 = json.loads(content2)
    print "keys in json_data_v2: "
    print parseKeys(json1)

    print 'keys in json_data_v1 yet not in json_data_v2: '
    print  diffKeys(json1 , json2,"2")
    # #
    # print 'keys in json_data_v2 yet not in json_data_v1: '
    # print diffKeys(json2, json1)