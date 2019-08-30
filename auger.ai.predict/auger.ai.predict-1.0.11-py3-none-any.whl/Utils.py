import inspect
import logging
import os
import sys
import traceback
import uuid
import json

from .FSClient import *

# For calculate_scores
from auger_ml.scores.regression import *
from auger_ml.scores.classification import *

def is_experimental_build():
    return True


def download_file(remote_path, local_dir = None, download_as_utf8=False, force_download=False):
    from urllib.request import urlopen
    import urllib
    import codecs
    try:
        from urllib.parse import urlparse, parse_qs
    except ImportError:
        from urlparse import urlparse, parse_qs

    logging.info("Reading file from url: %s" % remote_path)

    req = urlopen(remote_path)
    #print(req.info())

    if not local_dir:
        if download_as_utf8:
            return codecs.getreader('utf-8')(req, errors='replace')
        else:
            return req

    # Make local path        
    contentDisp = req.getheader('Content-Disposition')
    contentType = req.getheader('Content-Type')
    fileext = ''
    if contentType:
        if contentType == 'application/x-gzip':
            fileext = '.gz'
        elif contentType == 'text/csv':
            fileext = '.csv'

    filename = ''
    if contentDisp:
        items = contentDisp.split(';')
        for item in items:
            item = item.strip()
            if item.startswith("filename=\""):
                filename = item[10:-1]
                break
            elif item.startswith("filename="):
                filename = item[9:]
                break

    if not filename: 
        uri = urlparse(remote_path)
        params = parse_qs(uri.query)
        if len(params.get('id', []))>0:
            filename = params['id'][0]+fileext
        else:
            if len(uri.path)>0 and len(os.path.basename(uri.path))>0:
                filename = os.path.basename(uri.path)    
            else:
                filename = get_uid()+fileext

    local_file_path = os.path.join(local_dir, filename)

    download_file = True
    if not force_download and FSClient().isFileExists(local_file_path):
        remote_file_size = 0
        try:
            remote_file_size = int(req.getheader('Content-Length'))
        except:
            pass

        file_size = FSClient().getFileSize(local_file_path)
        #print(remote_file_size, file_size)
        if file_size == 0 or (remote_file_size > 0 and file_size != remote_file_size):
            logging.info("Local file with size %s is corrupted or outdated(remote file size: %s). Download again."%(file_size,remote_file_size))
            FSClient().removeFile(local_file_path)
        else:
            download_file = False

    req.close()        

    if download_file:
        logging.info("Download to local file path: %s"%local_file_path)
        FSClient().downloadFile(remote_path, local_file_path)

    return local_file_path
                    
def read_file_local_or_remote(local_path, remote_path):
    file_reader = None
    full_path = local_path
    if FSClient().isFileExists(local_path):
        file_reader = FSClient().open(local_path, "rb")
    else:
        if not remote_path:
            raise Exception(
                "File '%s' does not exist and there is no remote path." % local_path)

        #full_path = os.path.join(remote_path, os.path.basename(local_path))
        full_path = '/'.join([remote_path, os.path.basename(local_path)])
        file_reader = download_file(full_path, download_as_utf8=True)

    return file_reader, full_path


def process_arff_line(line, date_attrs):
    if "@attribute" in line.lower():
        parts = line.split(maxsplit=3)
        if len(parts) > 2 and parts[2].lower() == 'date':
            line = parts[0]+ ' ' + parts[1] + ' string\n'
            date_field = parts[1].strip("\"\'")
            date_format = parts[3].strip("\"\'\n")

            date_attrs[date_field] = date_format

    return line
            
def load_arff_header(arff_path, arff_folder_url=None):
    import arff

    file_reader, arff_path = read_file_local_or_remote(
        arff_path, arff_folder_url)
    strHeader = ""
    date_attrs = {}
    for line in file_reader:
        line = process_arff_line(line, date_attrs)        
        strHeader += line
        if "@data" in line.lower():
            break

    file_reader.close()

    dataArff = arff.loads(strHeader)
    features = []
    feature_types = []
    categoricals = {}

    for attr in dataArff['attributes']:
        features.append(str(attr[0]))
        feature_types.append(attr[1])
        if type(attr[1]) == list:
            categoricals[str(attr[0])] = attr[1]
        elif attr[1].lower() == 'string':
            if not str(attr[0]) in date_attrs:        
                categoricals[str(attr[0])] = []

    return arff_path, features, feature_types, categoricals, date_attrs

# def freeze_value(v):
#     if isinstance(v, dict):
#         return frozenset((k, freeze_value(v_)) for k, v_ in v.items())
#     if isinstance(v, (tuple, list)):
#         return tuple(freeze_value(v_) for v_ in v)
#     return v

# def get_pipeline_key(algorithm_name, algorithm_parameters):
#     #logging.info("get_pipeline_key: %s, %s"%(algorithm_name, algorithm_parameters))
#     return freeze_value((algorithm_name, algorithm_parameters))


# def hex_hash(key):
#     return '%016X' % (hash(key) % (2 * (sys.maxsize + 1)))


def get_uid():
    return uuid.uuid4().hex[:15].upper()


def remove_fields_from_dict(obj, fields_to_delete):
    for field in fields_to_delete:
        if field in obj:
            del obj[field]


def dict_equal_fields(dict1, dict2, names):
    for name in names:
        if dict1.get(name) != dict2.get(name):
            return False

    return True


def merge_dicts(d, other):
    from collections import Mapping

    for k, v in other.items():
        d_v = d.get(k)
        if isinstance(v, Mapping) and isinstance(d_v, Mapping):
            merge_dicts(d_v, v)
        else:
            d[k] = v


def convertStringsToUTF8(params):
    # if params is None:
    #     return params

    # if type(params) is dict:
    #     for key, value in params.items():
    #         new_key = key.encode('utf-8')
    #         del params[key]
    #         params[new_key] = convertStringsToUTF8(value)
    # elif type(params) is list:
    #     for idx, value in enumerate(params):
    #         params[idx] = convertStringsToUTF8(value)
    # elif type(params) is str:
    #     params = params.encode('utf-8')

    return params


def remove_dups_from_list(ar):
    from collections import OrderedDict
    return list(OrderedDict.fromkeys(ar))


def create_object_by_class(full_name, *args):
    import importlib

    module_name, class_name = full_name.rsplit('.', 1)
    cls = getattr(importlib.import_module(module_name), class_name)
    return cls(*args)


def parse_cluster_cpus(cpu_string, do_ceil=True):
    import math

    res = 1

    if not cpu_string:
        return res

    try:
        #logging.info("parse_cluster_cpus: %s"%cpu_string)

        if cpu_string.endswith('n'):
            res = float(cpu_string[:-1])
            res = res / 1e9
        elif cpu_string.endswith('u'):
            res = float(cpu_string[:-1])
            res = res / 1e6
        elif cpu_string.endswith('m'):
            res = float(cpu_string[:-1])
            res = res / 1e3
        else:
            res = float(cpu_string)

        if do_ceil:
            res = math.ceil(res)
        else:
            res = math.floor(res)

    except:
        logging.exception("parse_cluster_cpus failed:%s"%cpu_string)

    return max(int(res),1)

def convert_simple_numpy_type(obj):
    import numpy as np

    if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
        np.int16, np.int32, np.int64, np.uint8,
        np.uint16, np.uint32, np.uint64)):
        return int(obj)
    elif isinstance(obj, (np.float_, np.float16, np.float32, 
        np.float64)):
        return float(obj)

    # elif isinstance(obj,(np.ndarray,)): #### This is the fix
    #     return obj.tolist()
    
    return None

class NumpyJSONEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        res = convert_simple_numpy_type(obj)
        if res is not None:
            return res

        return json.JSONEncoder.default(self, obj)

def json_dumps_np(data, allow_nan=True):    
    return json.dumps(data, cls=NumpyJSONEncoder, allow_nan=allow_nan)

def convert_numpy_types(params):
    if params is None:
        return params

    if type(params) is dict:
        for key, value in params.items():
            params[key] = convert_numpy_types(value)
    elif type(params) is list:
        for idx, value in enumerate(params):
            params[idx] = convert_numpy_types(value)
    else:
        res = convert_simple_numpy_type(params)
        if res is not None:
            params = res

    return params

def calculate_scores(options, y_test, X_test=None, estimator=None, y_pred=None):
    from sklearn.metrics.scorer import get_scorer
    from sklearn.model_selection._validation import _score        
    from auger_ml.preprocessors.space import ppspace_is_timeseries_model
    import numpy as np

    if options['fold_group'] == 'time_series_standard_model':                
        pp_fold_groups_params = options.get('pp_fold_groups_params', {}).get(options['fold_group'], {})
        if pp_fold_groups_params.get('scale_target_min') and pp_fold_groups_params.get('scale_target_max'):
            corr_min = pp_fold_groups_params['scale_target_min']
            corr_max = pp_fold_groups_params['scale_target_max']

            if estimator:
                y_pred = estimator.predict(X_test)

            y_test = y_test * corr_max + corr_min
            if isinstance(y_pred, list):
                y_pred = np.array(y_pred)

            y_pred = y_pred * corr_max + corr_min
        else:
            logging.error("calculate_scores: no scaling found for target fold group: %s"%options['fold_group'])

    all_scores = {}
    for scoring in options.get('scoreNames', []):
        try:
            if ppspace_is_timeseries_model(options.get('algorithm_name')) and \
                scoring != options.get('scoring'):
                continue

            scorer = get_scorer(scoring)
            if y_pred is not None:
                all_scores[scoring] = scorer._sign * scorer._score_func(y_test, y_pred, **scorer._kwargs)
            else:
                all_scores[scoring] = _score(estimator, X_test, y_test, scorer)

            if np.isnan(all_scores[scoring]):
                all_scores[scoring] = 0

        except Exception as e:
            #logging.exception("Score failed.")
            if scoring == options.get('scoring', None):
                raise

            logging.error("Score %s for algorithm %s failed to build: %s" % (
                scoring, options.get('algorithm_name'), str(e)))
            all_scores[scoring] = 0

    return all_scores

# def load_arff_df_ex(path, csv_path=None):
#     import arff
#     import csv
#     fs_client = FSClient()
#     if csv_path is None:
#         csv_path = path + '.csv'
#     else:
#         fs_client.createFolder(csv_path)
#         csv_path = os.path.join(csv_path, os.path.basename(path) + '.csv')

#     if fs_client.isFileExists(csv_path):
#         return csv_path

#     strData = fs_client.readTextFile(path)
#     dataArff = arff.loads(strData, return_type=arff.COO)
#     strData = None
#     features = []
#     categorical = {}
#     maxCategories = 0

#     for attr in dataArff['attributes']:
#         features.append(attr[0])
#         if type(attr[1]) == list:
#             categorical[attr[0]] = attr[1]
#             if len(attr[1]) > maxCategories:
#                 maxCategories = max(len(attr[1]), maxCategories)

#     with fs_client.open(csv_path, mode="w") as csv_file:
#         csv_writer = csv.writer(csv_file, delimiter=',', escapechar="\\", quoting=csv.QUOTE_NONE)
#         csv_writer.writerow(features)

#         for item in dataArff['data']:
#             csv_writer.writerow(item)

#     return csv_path #, maxCategories, categorical

# def log_traceback(ex, ex_traceback=None):
#     if ex_traceback is None:
#         ex_traceback = ex.__traceback__
#     tb_lines = [line.rstrip('\n') for line in
#                 traceback.format_exception(ex.__class__, ex, ex_traceback)]
#     for l in tb_lines:
#         print(l)
