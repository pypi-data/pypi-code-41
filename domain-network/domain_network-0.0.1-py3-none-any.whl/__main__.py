#!/usr/bin/env python
# encoding: utf-8

"""CLI for Domain_Network project."""


from domainNetwork.domain_network_utils import *
from domainNetwork.tweet_reader import *
from domainNetwork.url_processor import *
from domainNetwork.network_generator import *

import argparse
import configparser
import glob



def parse_arguments():

    # parse arguments if available
    parser = argparse.ArgumentParser(
        description="Domain network"
    )

    # File path to the data.
    parser.add_argument(
        "--input_dir",
        type=str,
        help="File path to the dataset of tweets"
    )

    # File path to the config file.
    parser.add_argument(
        "--conf_dir",
        type=str,
        help="File path to the config file"
    )

    parser.add_argument(
        "--min_edge_weight",
        type=int,
        default=1,
        help="Minimum number of users that mention two netlocs together, to be shown in the network "
    )
    parser.add_argument(
        "--min_node_size",
        type=int,
        default=1,
        help="Minimum number of times a netloc is mentioned in total, to be shown in the network")
    parser.add_argument(
        "--min_stand_alone_size",
        default=1,
        type=int,
        help="Minimum number of times a stand-alone netloc is mentioned in total, to be shown in the network")

    #File pathes to output
    parser.add_argument(
        "--network_only",
        type=bool,
        default=False,
        help="Read preprocessed file and make a network, instead of reading row tweet files and preprocess it"
    )
    parser.add_argument(
        "--urls_file_name",
        type=str,
        default=None,
        help="File path to save urls including redirected ones"
    )

    parser.add_argument(
        "--network_output_file_name",
        type=str,
        default=None,
        help="File path to save network"
    )
    parser.add_argument(
        "--netloc_output_file_name",
        type=str,
        default=None,
        help="File path to save list of netlocs"
    )

    parser.add_argument(
        "--netloc_origin_output_file_name",
        type=str,
        default=None,
        help="File path to save original list of netlocs"
    )
    return parser


def main():
    parser = parse_arguments()
    args = parser.parse_args()

    # Read config file
    config = configparser.ConfigParser()
    config.read(args.conf_dir) # 'config/config.ini'

    print(config.sections())

    url_shorteners = config['FILTERING']['url_shortner_list']
    url_shortener_list =url_shorteners.strip('[]').split(',')

    nodes_to_remove  = config['FILTERING']['nodes_to_remove']
    nodes_list_to_remove =nodes_to_remove.strip('[]').split(',')

    dic = config['FILTERING']['replace_netlocs']
    dict_change_netlocs = json.loads(dic)


    if args.network_only:
        #Read processed url file
        df_urls = read_dataframe(args.urls_file_name)
        print("df_urls: ",df_urls.shape)

    else:
        #Read tweets and preprocess it
        path = args.input_dir
        all_files = glob.glob(path)
        df_tweets_origin = read_tweets(all_files)
        df_tweets = wide_to_long_url(df_tweets_origin)

        #Process URLs
        df_urls = process_urls(df_tweets, url_shortener_list, args.urls_file_name)

    domain_network = DomainNetwork(
        df_urls,
        nodes_list_to_remove,
        args.min_edge_weight,
        args.min_node_size,
        args.min_stand_alone_size,
        args.network_output_file_name,
        args.netloc_output_file_name,
        args.netloc_origin_output_file_name
    )

    domain_network.combine_nodes(dict_change_netlocs)
    domain_network.trim_nodes()

    domain_network.create_domain_network()
    domain_network.replace_nodes_in_network(dict_change_netlocs)
    domain_network.trim_domain()
    domain_network.add_stand_alone_node_to_network()
    domain_network.save_network()
    

# execute main function
if __name__ == "__main__":
    main()