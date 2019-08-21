# package subprocess manages calls to random walker
import subprocess
# package argparse manages the passing of arguments from terminal to code execution
import argparse
# package pickle allows to read/write files from/to binary format
import pickle
# progressbar package
import tqdm
# package gensim contains the word2vec model
from gensim.models import Word2Vec
from gensim.models.callbacks import CallbackAny2Vec
# To use multiprocessing on functions with more than 1 parameter
from functools import partial

#Trivial packages
import networkx as nx

import os
dirname = os.path.dirname(__file__)
print("dirname: ", dirname)

# Proprietary code
try:
    from GRAAF.utils import *
except:
    from graaf_tools.utils import *

# Logging is necessary to view detailed logs of Word2Vec progress
import logging
#logging.basicConfig(format="%(levelname)s - %(asctime)s: %(message)s", datefmt= '%H:%M:%S', level=logging.INFO)


#def build_network(traindata, artificialnodes):
#    G = nx.Graph()

#    edgelist1 = list((zip(traindata.transaction.values, traindata.client.values)))
#    edgelist2 = list((zip(traindata.transaction.values, traindata.merchant.values)))

#    if artificialnodes:
#        edgelist_fraud = list(zip(traindata.transaction.values, traindata.fraud.apply(lambda x: str(x)).values))
#        # Adding artificial node with fraud label
#        G.add_edges_from(edgelist_fraud)

    # Only one artificial node
    # edgelist_fraud = list(zip(traindata[traindata.fraud == True].transaction.values, traindata[traindata.fraud == True].fraud.apply(lambda x: str(x)).values))

#    G.add_edges_from(edgelist1)
#    G.add_edges_from(edgelist2)

#    logging.info("number of nodes: " + str(G.number_of_nodes()))
#    return G

#def invert_dict(d):
    #return dict([(v['label'], k) for k, v in d.items()])

class EpochLogger(CallbackAny2Vec):
    '''Callback to log information about training'''
    def __init__(self):
        self.epoch = 0
    def on_epoch_begin(self, model):
        print("Epoch #{} start".format(self.epoch))
    def on_epoch_end(self, model):
        print("Epoch #{} end".format(self.epoch))
        self.epoch += 1


def export_network(network, output_path):
    logging.info("Converting node labels to integers")
    G = nx.convert_node_labels_to_integers(network, first_label=0, ordering='default', label_attribute='label')
    logging.info("Exporting edgelist")
    nx.write_edgelist(G, output_path+"output_edgelist.csv", comments='#', delimiter=' ', data=False, encoding='utf-8')

    node_dict = dict(G.nodes(data='label'))
    dict_node = invert_dict(node_dict)

    filename = output_path+"dict_node_" + ".pkl"
    with open(filename, 'wb') as handle:
        pickle.dump(dict_node, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return dict_node

class Node2Vec():

    def __init__(self, network, workers=3, output_path='./tmp/', verbose=True):
        self.network = network
        self.workers = workers
        self.output_path = output_path
        self.verbose = verbose


    def random_walking(self, random_walking_path, number_of_walks, length_of_walks):

        logging.info("Converting node labels to integers")
        self.network_int = nx.convert_node_labels_to_integers(self.network, first_label=0, ordering='default', label_attribute='label')

        logging.info("Exporting edgelist")
        nx.write_edgelist(self.network_int, self.output_path + "output_edgelist.csv", comments='#', delimiter=' ', data=False,
                          encoding='utf-8')

        p = random_walking_path +'convert.py'
        command = "python3 " + p + " --undirected " + self.output_path + "output_edgelist.csv " + self.output_path + "output_edgelist_binary"

        FNULL = open(os.devnull, 'w')
        if self.verbose:
            p1 = subprocess.Popen(command, shell=True)
        else:
            p1 = subprocess.Popen(command, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        p1.wait()

        logging.info("finished conversion")
        logging.info("start walking")
        p = random_walking_path + 'randomwalk'
        command = p + " -threads " + str(self.workers) + " -nwalks " + str(
            number_of_walks) + " -walklen " + str(
            length_of_walks) + " -input " + self.output_path + "output_edgelist_binary -output " + self.output_path + "output_walks"
        p2 = subprocess.Popen(command, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        p2.wait()

    def generate_embeddings(self, embedding_dimension, cbow=False, **kwargs):

        epoch_logger = EpochLogger()
        self.embeddings = Word2Vec(corpus_file= self.output_path + "output_walks", size=embedding_dimension,
                              min_count=1, callbacks=[epoch_logger], batch_words=100, workers=self.workers,
                              sg = not cbow, **kwargs)

        # Add the embeddings to the nodes as attribute information
        node_dict = dict(self.network_int.nodes(data='label'))
        #dict_node = invert_dict(node_dict)
        nx.set_node_attributes(self.network, {node_dict[i]: {'embedding': self.embeddings.wv[str(i)]} for i in self.network_int.nodes()})

        # Return the embeddings in a pandas DataFrame as well
        return pd.DataFrame().from_dict({node_dict[i]: self.embeddings.wv[str(i)] for i in self.network_int.nodes()}, orient='index')

def prepare_baseline(input_path, output_path, workers=3, walknum=10, walklen=20, dim=32, artificialnodes=False, cbow=1):
    """
    :param baseline_df:
    :return:
    """
    #Save original working directory
    owd = dirname

    # Get dataset
    baseline_df = pd.read_csv(input_path)
    # Build the network
    G = build_network(baseline_df, artificialnodes)
    dict_node = export_network(G, output_path)

    #filename = "temp/dict_node_" + start_of_data.strftime('%d%m%Y') + ".pkl"
    #with open(filename, 'wb') as handle:
        #pickle.dump(dict_node, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # Convert the nodes
    p = os.path.join(dirname, '../binary_conversion/convert.py')
    command = "python3 "+p+" --undirected "+output_path+"output_edgelist.csv "+output_path+"output_edgelist_binary"
    p1 = subprocess.Popen(command, shell=True)
    p1.wait()

    logging.info("finished conversion")
    logging.info("start walking")
    p = os.path.join(dirname, '../random_walk/randomwalk')
    command = p+" -threads " + str(workers) + " -nwalks " + str(
        walknum) + " -walklen " + str(
        walklen) + " -input "+ output_path+"output_edgelist_binary -output "+ output_path+"output_walks"
    p2 = subprocess.Popen(command, shell=True)
    p2.wait()

    walks = output_path + "output_walks"

    # Run Word2vec
    print('cbow: ', cbow)
    embeddings = training_embeddings(walks, dim, cbow, workers)

    # export embeddings
    retrieve_embeddings(baseline_df, embeddings, dict_node, output_path)

    baseline_df.to_csv(output_path+"baseline_df_embeddings.csv")

def training_embeddings(**kwargs):
    ### GENSIM ###

    epoch_logger = EpochLogger()
    embeddings = Word2Vec(min_count=1, callbacks=[epoch_logger], batch_words=100, **kwargs)
    #corpus_file=walks, size=dim, workers=workers,  sg=cbow
    return embeddings


def get_embeddings_dict(df, embeddings, dict_node, node_cat):


    # Create empty dict
    embed_dict = {}

    for i, row in df.iterrows():
        trans = row[node_cat]

        node_number = dict_node[trans]

        emb_trans = embeddings.wv[str(node_number)]
        embed_dict[trans] = emb_trans

    #embed = pd.DataFrame()
    #embed = embed.from_dict(embed_dict, orient='index')
    #embed.reset_index(drop=True, inplace=True)

    return embed_dict



def retrieve_embeddings(df, embeddings, dict_node, output_path):
    logging.info("Retrieving embeddings for transactions")
    get_embeddings_p = partial(get_embeddings_dict, embeddings=embeddings, dict_node=dict_node, node_cat="transaction")
    embeds_transaction_list = multiproc(df, get_embeddings_p, result_is_not_a_frame=True)
    embeds_transaction = list_of_dict_to_dict(embeds_transaction_list)
    logging.info("Retrieving embeddings for cardholders")
    get_embeddings_p = partial(get_embeddings_dict, embeddings=embeddings, dict_node=dict_node, node_cat="client")
    embeds_client_list = multiproc(df, get_embeddings_p, result_is_not_a_frame=True)
    embeds_client = list_of_dict_to_dict(embeds_client_list)
    logging.info("Retrieving embeddings for merchants")
    get_embeddings_p = partial(get_embeddings_dict, embeddings=embeddings, dict_node=dict_node, node_cat="merchant")
    embeds_merchant_list = multiproc(df, get_embeddings_p, result_is_not_a_frame=True)
    embeds_merchant = list_of_dict_to_dict(embeds_merchant_list)

    logging.info("outputting embeddings to csv files")

    filename = output_path + "embeds_client.pkl"
    with open(filename, 'wb') as handle:
        pickle.dump(embeds_client, handle, protocol=pickle.HIGHEST_PROTOCOL)

    filename = output_path + "embeds_merchant.pkl"
    with open(filename, 'wb') as handle:
        pickle.dump(embeds_merchant, handle, protocol=pickle.HIGHEST_PROTOCOL)

    filename = output_path + "embeds_transaction.pkl"
    with open(filename, 'wb') as handle:
        pickle.dump(embeds_transaction, handle, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', help="location of the training dataset")
    parser.add_argument('--output_path', default='../temp/', help="location reserved for the embeddings")
    parser.add_argument('--workers', default=3, help="available cores for parallel processing")
    parser.add_argument('--walknum', default=10)
    parser.add_argument('--walklen', default=20)
    parser.add_argument('--dim', type=int, default=32)
    parser.add_argument('--training', default=4, help='number of days of data to use as training data')
    parser.add_argument('--test', default=1, help='number of days of data to use as test data')
    parser.add_argument('--polyaxon', default=False, help='boolean indicating whether datasystem should be fetched ')
    parser.add_argument('--algorithm', default=1, help='1 for skipgram, 0 for CBOW')
    parser.add_argument('--artificialnodes', default=False)

    args = parser.parse_args()
    #baseline = args.training
    #updategran = args.training + args.test

    input_path = args.input_path
    output_path = args.output_path
    workers = args.workers
    walknum = args.walknum
    walklen = args.walklen
    dim = args.dim
    artificialnodes = args.artificialnodes
    cbow = args.algorithm

    datetime_column = 'timestamp'
    #timegran = datetime.timedelta(days=1)

    #start_of_data = pd.to_datetime(args.start, dayfirst=True)  # type: object
    #baseline = baseline*timegran
    #updategran = updategran*timegran
    #datetime_col = datetime_column

    if args.polyaxon:
        from polyaxon_client.tracking import Experiment, get_data_paths
        from polystores.stores.manager import StoreManager

        experiment = Experiment()
        store = StoreManager(path=get_data_paths()['boucquet2'])
        store.download_file('input.csv', 'input.csv')
        df = pd.read_csv("input.csv", index_col=0, parse_dates=['timestamp'])
    else:
        df = pd.read_csv(args.output_path+"input.csv", index_col=0, parse_dates=['timestamp'])

    aucs = []

    #os.chdir('..')
    prepare_baseline(input_path, output_path, workers, walknum, walklen, dim, artificialnodes, cbow)
