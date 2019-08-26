# -*- coding:utf-8 -*-
import os
import base64
import hashlib
import json
import time
import math

def ceil(f):
    return int(math.ceil(f))

def human_info(data):
    if type(data) == dict: # pylint: disable=C0123
        ret = '{'
        for k, v in data.items():
            ret += str("%s:%s, " % (human_info(k), human_info(v)))
        ret += '}'

    elif type(data) == list: # pylint: disable=C0123
        ret = '['
        for i in range(len(data)):
            ret += '%s,' % human_info(data[i])
        ret += ']'

    elif type(data) == tuple: # pylint: disable=C0123
        ret = '('
        for i in range(len(data)):
            ret += '%s,' % human_info(data[i])
        ret += ')'

    elif type(data) == unicode: # pylint: disable=C0123
        ret = data.encode('utf-8')
        ret = str("'%s'" % ret)
    elif type(data) == str: # pylint: disable=C0123
        ret = str("'%s'" % data)
    else:
        ret = str(data)

    return ret


def get_val_ex(_dict, _key, dft_val):
    if _key not in _dict:
        return dft_val
    else:
        return _dict[_key]

def get_hour_delta(time_str):
    ts = time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S'))
    now = time.time()
    return (now - ts) / 3600

def json_read(jdata):
    return transcode(json.loads(jdata))

def json_write(data):
    return json.dumps(data)

def filter_id(data_list):
    for d in data_list:
        del d['_id']
    return data_list

def get_md5(src):
    myMd5 = hashlib.md5()
    myMd5.update(src)
    myMd5_Digest = myMd5.hexdigest()
    return myMd5_Digest

def file_md5(path):
    src = open(path).read()
    return get_md5(path)


def get_suffix(filename):
    segs = os.path.split(filename)
    return os.path.splitext(segs[1])[1]

def transcode(data):
    if type(data) == dict: # pylint: disable=C0123
        for k, v in data.items():
            del data[k]
            data[transcode(k)] = transcode(v)

    elif type(data) == list: # pylint: disable=C0123
        for i in range(len(data)):
            data[i] = transcode(data[i])

    elif type(data) == unicode: # pylint: disable=C0123
        data = data.encode('utf-8')

    return data

def encode_name(name):
    seg = name.split('-')
    seg[1] = base64.b64encode(seg[1])
    name = seg[0] + '-' + seg[1]
    return name

def decode_name(name):
    seg = name.split('-')
    seg[1] = base64.b64decode(seg[1])
    name = seg[0] + '-' + seg[1]
    return name

def separate_file_name(file_name):
    try:
        idx = file_name.index('.')
        part1 = file_name[:idx]
        image_type = file_name[idx+1:]

        idx = part1.rindex('_')
        seq = part1[idx+1:]
        part1 = part1[:idx]

        idx = part1.rindex('_')
        tpe = part1[idx+1:]
        tpid = part1[:idx]
        return tpid, tpe, seq, image_type
    except Exception, e: # pylint: disable=W0703
        return None


_file_type_dict = {}
_file_type_dict['png'] = 'image/png'
_file_type_dict['webp'] = 'image/webp'
_file_type_dict['jpg'] = 'image/jpeg'
_file_type_dict['jpeg'] = 'image/jpeg'
_file_type_dict['jpe'] = 'image/jpeg'
_file_type_dict['gz'] = 'application/x-gzip'
_file_type_dict['txt'] = 'text/plain'
_file_type_dict['pb'] = 'application/octet-stream'

def filetype_valid(file_type):
    return file_type in _file_type_dict

def filetype2contenttype(file_type):
    if file_type in _file_type_dict:
        return _file_type_dict[file_type]
    else:
        return None

def str_to_bool(string):
    return string.lower() == 'true'

def bool_to_str(boolean):
    return 'True' if boolean else 'False'

def main():
    print separate_file_name('114_20170621133647894_00_003.jpg')
    print separate_file_name('129_20170621132818068_02_000.yml.gz')

if __name__ == '__main__':
    main()
