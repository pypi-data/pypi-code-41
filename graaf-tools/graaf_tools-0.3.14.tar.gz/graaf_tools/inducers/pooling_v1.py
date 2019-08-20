#!/usr/bin/env python
# coding: utf-8


import datetime
import os
import pickle
import logging
# To use multiprocessing on functions with more than 1 parameter
from functools import partial
os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
from GRAAF.utils import *


def embeddings_to_frame(d, embeds_transaction):

    '''
    This function concats the original dataframe with the embeddings for each transaction
    '''

    transaction_emb = dict()

    for i, row in d.iterrows():
        transaction_emb[i] = embeds_transaction[row['transaction']]

    transaction_frame = pd.DataFrame().from_dict(transaction_emb, orient='index')



    return transaction_frame


def induce_embeddings(d, embeds_transaction, embeds_client, embeds_merchant, overall_mean):

    '''
    :param d: testset dataframe
    :param embeds_transaction: dataframe with transaction embeddings
    :param overall_mean: overall mean embedding
    :param dict_transaction:
    :param baseline_df:
    :param NN_NEIGHBORS: number of neighbors to consider in the NN algorithm
    :return: dataframe containing an embedding corresponding to each transaction in the testset
    '''

    known_clients = embeds_client.keys()
    known_merchants = embeds_merchant.keys()

    transaction_emb = dict()

    for i, row in d.iterrows():

        client_bool = False
        merchant_bool = False

        client = row['client']
        merchant = row['merchant']
        # step 1: have we seen the client before?
        if (client in known_clients):
            client_bool = True
        # step2: have we seen the merchant before?
        if (merchant in known_merchants):
            merchant_bool = True

        if (client_bool)&(merchant_bool):
            transaction_emb[i] = (embeds_client[client] + embeds_merchant[merchant])/2

        elif client_bool:
            transaction_emb[i] = embeds_client[client]
        elif merchant_bool:
            transaction_emb[i] = embeds_merchant[merchant]
        else:
            transaction_emb[i] = overall_mean


    #client_cols = ['m'+str(i) for i in range(dim)]
    #merchant_cols = ['c'+str(i) for i in range(dim)]
    transaction_frame = pd.DataFrame()
    transaction_frame = transaction_frame.from_dict(transaction_emb, orient='index')
    #merchant_frame = pd.DataFrame()
    #merchant_frame = merchant_frame.from_dict(merchant_emb, orient='index', columns=merchant_cols)
    #concatenated = client_frame.merge( merchant_frame, left_index=True, right_index=True)
    return transaction_frame



def load_csv_to_df(filename, input_path = '../../temps/1_32_20_10_noartificialnodes/original_embeddings/'):


    df = pd.read_csv(input_path+filename)

    return df


def run(embeds_client_df, embeds_merchant_df, embeds_transaction_df,
        baseline_df, day_df, output_path='../../temp/1_32_20_10_noartificialnodes/',
        verbose=1, WORKERS=3):

    #Log execution time
    st = time.time()

    #Calculating the overall mean embedding
    logging.info('Step 1: Calculating overall mean embedding')
    embeds_df = pd.concat([embeds_client_df, embeds_merchant_df, embeds_transaction_df])
    overall_mean = embeds_df.mean(axis=0).values

    logging.info('Step 2: Retrieving embeddings for training dataset.')
    baseline_df_embeddings = baseline_df.merge(embeds_transaction_df, how='left', left_on='transaction',  right_index=True,
                    sort=False, suffixes=('_x', '_y'))
    logging.info('Saving training dataset for classifier.')
    baseline_df_embeddings.to_pickle(output_path+'baseline_df_embeddings.pkl')

    logging.info('Step 5: Creating new embeddings for test dataset based on Pooling.')
    embeds_transaction = embeds_transaction_df.T.to_dict('list')
    embeds_transaction = {k: np.array(v) for k, v in embeds_transaction.items()}
    
    embeds_client = embeds_client_df.T.to_dict('list')
    embeds_client = {k: np.array(v) for k, v in embeds_client.items()}
    
    embeds_merchant = embeds_merchant_df.T.to_dict('list')
    embeds_merchant = {k: np.array(v) for k, v in embeds_merchant.items()}
    
    induce_embeddings_p = partial(induce_embeddings, embeds_transaction=embeds_transaction, embeds_client=embeds_client, embeds_merchant=embeds_merchant, overall_mean=overall_mean)
    day_df_embeddings = multiproc(day_df, induce_embeddings_p, workers=WORKERS)
    day_df_embeddings = day_df_embeddings.merge(day_df, how='left', left_index=True, right_index=True, validate="one_to_one")
    day_df_embeddings.to_pickle(output_path+'day_df_embeddings.pkl')

    ed = time.time()
    logging.info('Runtime of process: '+str(ed-st))
