import multiprocessing
import time as time
import pandas as pd
import tqdm
import pickle
import numpy as np
from collections import OrderedDict
import os
import json
from google.cloud import storage
import logging

def multiproc(df, function, result_is_not_a_frame=False, workers=3, n_chunks=50, custom_chunks=None):

    """takes a pandas dataframe and applies a function in parallel by
    dividing the dataframe in multiple chunks

    Args:
        df: The dataframe to process.
        function: The function to apply in parallel.
        result_is_not_a_frame: boolean parameter, will avoid merging the parallel results into a dataframe.
    Returns:
        Either returns the processed dataframe or the collection of parallel results.
    """
    
    num_processes = workers#(multiprocessing.cpu_count()-1)
    chunk_size = int(df.shape[0]/n_chunks)
    
    if custom_chunks:
        chunks = custom_chunks
    else:
        chunks = [df.iloc[i:i + chunk_size] for i in range(0, df.shape[0], chunk_size)]
    
    pool = multiprocessing.Pool(processes=num_processes)
    if result_is_not_a_frame:
        result = list(tqdm.tqdm(pool.imap(function, chunks), total=len(chunks)))
    else:
        #result = pd.concat(pool.map(function, chunks))
        result = pd.concat(list(tqdm.tqdm(pool.imap(function, chunks), total=len(chunks))))

    pool.close()
    pool.join()

    return result


def invert_dict(d):
    """ inverts keys and values in dictionary, use with care!

    Args:
        d: dictionary to invert.

    Returns:
        Dictionary with keys and values swapped.
    """
    return dict([(v, k) for k, v in d.items()])



def list_of_dict_to_dict(list_of_dicts):
    result = {}
    for d in list_of_dicts:
        result.update(d)
    return result

def get_baseline_datasets(df, start_of_data):
    start_of_day = start_of_data + baseline

    baseline_df = df[(df[datetime_col] <= start_of_day) & (df[datetime_col] >= start_of_data)]

    return baseline_df


def get_day_datasets(df, start_of_data):
    start_of_day = start_of_data + baseline
    end_of_day = start_of_day + timegran

    day_df = df[(df[datetime_col] > start_of_day) & (df[datetime_col] <= end_of_day)]

    return day_df




def prepare_day(df, start_of_data):
    # Get dataset of day
    day_df = get_day_datasets(df, start_of_data)
    day_df.to_csv(args.output_path+"/day_df_" + start_of_data.strftime('%d%m%Y') + '.csv')

def load_pkl_to_df(filename, input_path = '../../temps/1_32_20_10_noartificialnodes/original_embeddings/'):

    with open(input_path+filename, 'rb') as handle:
        file = pickle.load(handle)

    if isinstance(file, dict):
        df = pd.DataFrame().from_dict(file, orient='index')
    elif isinstance(file, pd.DataFrame):
        df = file
    else:
        raise Exception('input file format is not recognised: {}'.format(type(file)))

    return df

def download_file(filename, path, bucket_name='fraud_data_nn_approach'):
    
    try:
        os.makedirs(path)
    except:
        pass
    
    if os.path.isfile(os.path.join(path, filename)):
        logging.info('file already here')
    else:
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(os.path.join(path,filename))
        print(os.path.join(path,filename))
        blob.download_to_filename(os.path.join(path,filename))

def download_folder(remotepath, bucket_name='fraud_data_nn_approach'):

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=remotepath)  # Get list of files
    for blob in blobs:
        *path, filename = blob.name.split('/')
        print('path: ', path)
        print('filename: ', filename)
        path = '/'.join(path)
        download_file(filename, path, bucket_name=bucket_name)
        #filename = blob.name.replace('/', '_')
        #blob.download_to_filename(localpath + filename)  # Download

def upload_file(localpath, remotepath, bucket_name='fraud_data_nn_approach'):
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(remotepath)
        blob.upload_from_filename(localpath)

def upload_folder(localpath, remotepath, bucket_name='fraud_data_nn_approach'):

    for filename in tqdm.tqdm(os.listdir(localpath)):
        upload_file(os.path.join(localpath, filename), os.path.join(remotepath, filename), bucket_name)

#----#

def filename_decoder(df, exception=None):
    filenames = set(df.filename)
    data=dict()
    i = 0
    for original_filename in filenames:
        newrow = dict()
        filename = original_filename


        if (filename[0] == '1')|(filename[0] == '4'):
            newrow['baseline'] = filename[0]
            newrow['dimension'] = filename[2:4]
            newrow['walk length'] = filename[5:7]
            newrow['walk number'] = filename[8:10]
            filename = filename[11:]
        else:
            newrow['baseline'] = ''
            newrow['dimension'] = ''
            newrow['walk length'] = ''
            newrow['walk number'] = ''

        #Graph architecture
        if filename[0:17] == 'noartificialnodes':
            newrow['graph'] = 'no artificial nodes'
            filename = filename[18:]
        elif filename[0:9] == 'onlyfraud':
            newrow['graph'] = 'only fraud node'
            filename = filename[10:]
        else:
            newrow['graph'] = 'both fraud and non-fraud artificial node'


        ## Setting
        if filename[:6] == 'concat':
            newrow['setting'] = 'concatenation'
            filename = filename[7:]
        if filename[:2] == 'nn':
            newrow['setting'] = 'nearest neighbour'
            filename = filename[3:]

        if filename[:29] == 'pooling_transactions_training':
            newrow['setting'] = 'pooling transactions training'
            filename = filename[30:]

        if filename[:26] == 'pooling_inductive_training':
            newrow['setting'] = 'pooling inductive training'
            filename = filename[27:]

        if filename[:9] == 'prevtrans':
            newrow['setting'] = 'previous transaction'
            filename = filename[10:]

        if filename[:30] == "hadamard_transactions_training":
            newrow["setting"] = 'hadamard transactions training'
            filename = filename[31:]

        if filename[:27] == "hadamard_inductive_training":
            newrow["setting"] = 'hadamard inductive training'
            filename = filename[28:]

        if filename[:24] == "L1_transactions_training":
            newrow["setting"] = 'L1 transactions training'
            filename = filename[25:]

        if filename[:21] == "L1_inductive_training":
            newrow['setting'] = 'L1 inductive training'
            filename = filename[22:]

        if filename[:24] == "L2_transactions_training":
            newrow["setting"] = 'L2 transactions training'
            filename = filename[25:]

        if filename[:21] == "L2_inductive_training":
            newrow['setting'] = 'L2 inductive training'
            filename = filename[22:]

        if exception == 'graphsage_maxpool':
            newrow['setting'] = 'graphsage maxpool'
        if exception == 'graphsage_meanpool':
            newrow['setting'] = 'graphsage meanpool'
        if exception == 'pagerank':
            newrow['setting'] = 'pagerank'



        if filename[20] == '0':
            newrow['undersampling_ratio'] = 0
            if filename[21] == '_':
                filename = filename[22:]
            else:
                filename = filename[21:]

        else:
            newrow['undersampling_ratio'] = filename[20:23]
            if filename[23] == '_':
                filename = filename[24:]
            else:
                filename = filename[23:]


        if filename[23] == 'S':
            newrow['oversampling_algorithm'] = 'SMOTE'
            if filename[28]=='_':
                filename = filename[29:]
            else:
                filename = filename[28:]

        elif filename[23] == 'A':
            newrow['oversampling_algorithm'] = 'ADASYN'
            if filename[29]=='_':
                filename = filename[30:]
            else:
                filename = filename[29:]
        elif filename[23] == 'R':
            newrow['oversampling_algorithm'] = 'RandomOverSampler'
            if filename[40]=='_':
                filename = filename[41:]
            else:
                filename = filename[40:]
        else:
            newrow['oversampling_algorithm'] = ''
            if(filename[23] == '_'):
                filename = filename[24:]
            else:
                filename = filename[23:]




        if filename[19] == '0':
            newrow['oversampling_ratio'] = 0
            filename = filename[21:]
        else:
            newrow['oversampling_ratio'] = filename[19:22]
            filename = filename[23:]

        #print(filename)
        if filename[0] == 'l':
            newrow['predictive algorithm'] = 'logistic_regression'
        if filename[0] == 'r':
            newrow['predictive algorithm'] = 'random_forest'
        if filename[0] == 'X':
            newrow['predictive algorithm'] = 'XGBoost'
        if filename[0] == 'S':
            newrow['predictive algorithm'] = 'SVM'


        filename = original_filename
        # Add auc
        newrow['average_auc'] = df[(df.filename==filename)&(df.result == 'auc')].average.values[0]
        newrow['stdev_auc'] = df[(df.filename==filename)&(df.result == 'auc')].stdev.values[0]
        # Add F1
        newrow['average_f1'] = df[(df.filename==filename)&(df.result == 'f1')].average.values[0]
        newrow['stdev_f1'] = df[(df.filename==filename)&(df.result == 'f1')].stdev.values[0]
        # Add Lift
        try:
            newrow['average_lift'] = df[(df.filename==filename)&(df.result == 'lift@10%')].average.values[0]
            newrow['stdev_lift'] = df[(df.filename==filename)&(df.result == 'lift@10%')].stdev.values[0]
        except:
            pass


        # Add original values
        for j in range(5):
            newrow['auc_iter_'+str(j)] = df[(df.filename==filename)&(df.result == 'auc')].loc[:,[j]].values[0][0]
            newrow['f1_iter_'+str(j)] = df[(df.filename==filename)&(df.result == 'f1')].loc[:,[j]].values[0][0]
            newrow['lift_iter_'+str(j)] = df[(df.filename==filename)&(df.result == 'lift@10%')].loc[:,[j]].values[0][0]

        data[i] = newrow
        i += 1

    result = pd.DataFrame()
    result = result.from_dict(data, orient='index')
    return result


def Diff(li1, li2): 
    return (list(set(li1) - set(li2))) 