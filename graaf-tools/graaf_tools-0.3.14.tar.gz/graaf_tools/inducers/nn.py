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
from graaf_tools.utils import *


def embeddings_to_frame(d, embeds_transaction):

    '''
    This function concats the original dataframe with the embeddings for each transaction
    '''

    transaction_emb = dict()

    for i, row in d.iterrows():
        transaction_emb[i] = embeds_transaction[row['transaction']]

    transaction_frame = pd.DataFrame().from_dict(transaction_emb, orient='index')



    return transaction_frame


def induce_embeddings(d, embeds_transaction, overall_mean, dict_transaction, baseline_df, NN_NEIGHBORS):

    '''
    :param d: testset dataframe
    :param embeds_transaction: dataframe with transaction embeddings
    :param overall_mean: overall mean embedding
    :param dict_transaction:
    :param baseline_df:
    :param NN_NEIGHBORS: number of neighbors to consider in the NN algorithm
    :return: dataframe containing an embedding corresponding to each transaction in the testset
    '''

    # list of all clients/merchants which had transactions in the 'baseline' dataset
    prev_trans = dict_transaction.keys()
    zero_index = d.index[0]
    shape = d.shape[0]
    a = 0

    transaction_emb = dict()

    for i, row in d.iterrows():

        # Progress tracking overhead
        #prog = ((i-zero_index)/shape)*100
        #if prog > a:
         #   print(prog)
         #   a += 10

        client_bool = False
        merchant_bool = False

        client = row['client']
        merchant = row['merchant']
        # step 1: have we seen the client before?
        if (client in prev_trans):
            client_bool = True
        # step2: have we seen the merchant before?
        if (merchant in prev_trans):
            merchant_bool = True

        if (client_bool)&(merchant_bool):

            client_transactions = dict_transaction[client][-NN_NEIGHBORS:]
            merchant_transactions = dict_transaction[merchant][-NN_NEIGHBORS:]

            nearest_client_transaction = nn_neigh(client_transactions, baseline_df, row)
            nearest_merchant_transaction = nn_neigh(merchant_transactions, baseline_df, row)

            transaction_emb[i] = (embeds_transaction[nearest_client_transaction] + embeds_transaction[nearest_merchant_transaction])/2
            transaction_emb[i] = np.append(transaction_emb[i], ['both'])

        elif client_bool:

            client_transactions = dict_transaction[client][-NN_NEIGHBORS:]
            nearest_client_transaction = nn_neigh(client_transactions, baseline_df, row)
            transaction_emb[i] = embeds_transaction[nearest_client_transaction]
            transaction_emb[i] = np.append(transaction_emb[i], ['only_client'])

        elif merchant_bool:

            merchant_transactions = dict_transaction[merchant][-NN_NEIGHBORS:]
            nearest_merchant_transaction = nn_neigh(merchant_transactions, baseline_df, row)
            transaction_emb[i] = embeds_transaction[nearest_merchant_transaction]
            transaction_emb[i] = np.append(transaction_emb[i], ['only_merchant'])
        else:

            transaction_emb[i] = overall_mean
            transaction_emb[i] = np.append(transaction_emb[i], ['none'])

    transaction_frame = pd.DataFrame()
    transaction_frame = transaction_frame.from_dict(transaction_emb, orient='index')

    return transaction_frame



def load_csv_to_df(filename, input_path = '../../temps/1_32_20_10_noartificialnodes/original_embeddings/'):


    df = pd.read_csv(input_path+filename)

    return df

def run(embeds_client_df, embeds_merchant_df, embeds_transaction_df,
        train_df, val_df, test_df, output_path='../../temp/1_32_20_10_noartificialnodes/',
        WORKERS=3, NN_NEIGHBORS=5):

    #Log execution time
    st = time.time()

    #Calculating the overall mean embedding
    logging.info('Step 1: Calculating overall mean embedding')
    embeds_df = pd.concat([embeds_client_df, embeds_merchant_df, embeds_transaction_df])
    overall_mean = embeds_df.mean(axis=0).values

    #Make sure the data is suitable for NN algorithm
    logging.info('Step 2: Preparing for nearest neighbors')
    train_df = prepare_for_nn(train_df)
    val_df = prepare_for_nn(val_df)
    test_df = prepare_for_nn(test_df)

    logging.info('Step 3: Loading a dictionary containing previous transactions for each cardholder and merchant.')
    dict_transaction = get_transactions_of(train_df)

    logging.info('Step 4: Retrieving embeddings for training dataset.')
    train_df_embeddings = train_df.merge(embeds_transaction_df, how='left', left_on='transaction',  right_index=True,
                    sort=False, suffixes=('_x', '_y'))
    logging.info('Saving training dataset for classifier.')
    #baseline_df_embeddings.to_pickle(output_path+'train_df_embeddings.pkl')

    logging.info('Step 5: Creating new embeddings for test dataset based on NN.')
    embeds_transaction = embeds_transaction_df.T.to_dict('list')
    embeds_transaction = {k: np.array(v) for k, v in embeds_transaction.items()}
    induce_embeddings_p = partial(induce_embeddings, embeds_transaction=embeds_transaction, overall_mean=overall_mean, dict_transaction=dict_transaction, baseline_df=train_df, NN_NEIGHBORS=NN_NEIGHBORS)

    val_df_embeddings = multiproc(val_df, induce_embeddings_p, workers=WORKERS)
    test_df_embeddings = multiproc(test_df, induce_embeddings_p, workers=WORKERS)
    val_df_embeddings = val_df_embeddings.merge(val_df, how='left', left_index=True, right_index=True, validate="one_to_one")
    test_df_embeddings = test_df_embeddings.merge(test_df, how='left', left_index=True, right_index=True, validate="one_to_one")
    #day_df_embeddings.to_pickle(output_path+'day_df_embeddings.pkl')

    ed = time.time()
    logging.info('Runtime of process: '+str(ed-st))

    return (train_df_embeddings, val_df_embeddings, test_df_embeddings)



## NN specific functions

def prepare_for_nn(bdf):
    bdf['category'] = bdf.category.astype('category')
    bdf['timestamp'] = pd.to_datetime(bdf.timestamp)
    return bdf

def get_transactions_of(d, columns=['client','merchant'], COL_NAME_TRANSACTION='transaction'):
    '''
    Returns a dictionary containing for each category in 'columns' a list of transactions.
    :param d: DataFrame with client, merchant and
    :return: dictionary with for each client and merchant an entry containing the list of previous transactions.
    '''
    dict_transactions = {}

    for cat in columns:
        for i, row in d.iterrows():

            transaction = row[COL_NAME_TRANSACTION]
            entity = row[cat]

            if entity in dict_transactions.keys():
                entity_trans = dict_transactions[entity]
            else:
                entity_trans = []

            entity_trans.append(transaction)
            dict_transactions[entity] = entity_trans

    return dict_transactions

def nn_neigh(transactions, df, row):
    '''
    :param transactions: list of transaction identifiers among which we search the nearest neighbor to the transaction
    in current row.
    :param df: DataFrame
    :param row: DataFrame row associated with the current transaction.
    :return: return the transaction identifier of the nearest neighbor.
    '''


    # From all past transactions, take those which are related to this client or merchant (hence, are in the transaction index list)
    nndf = df[(df.transaction.isin(transactions))]
    # We will do some cool transformations to this dataset before applying NN. To make sure we can compute distances to other transactions
    # This row will have to undergo the same transformations, hence we append it to the data
    nndf = nndf.append(row)
    # drop some unnecessary columns
    nndfd = nndf.drop(['transaction'], axis=1)
    nndfd = nndfd.drop(['timestamp'], axis=1)

    # split the numerical and categorical columns.
    nndf_num = nndfd.loc[:,['amount']]
    nndf_dum = nndfd.loc[:,['client', 'merchant', 'category', 'country']]

    # get dummies
    nndf_dum  = pd.get_dummies(nndf_dum, drop_first=True)

    # standardize the numerical features
    nndf_num = MinMaxScaler().fit_transform(nndf_num)


    # concat both categorical and numerical features
    nndfc = np.concatenate((nndf_num, nndf_dum), axis=1)
    #print(nndfc[:5])
    # train nn on all but last row
    nn = NearestNeighbors()
    nn.fit(nndfc[:-1])
    # find nearest neighbor of last row
    nns = nn.kneighbors(nndfc[-1].reshape(1, -1), n_neighbors=1)

    #print(nns[0])

    return nndf.iloc[nns[1][0]].transaction.values[0]
