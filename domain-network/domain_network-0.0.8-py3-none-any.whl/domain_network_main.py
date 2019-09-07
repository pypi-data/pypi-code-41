#!/usr/bin/env python
# encoding: utf-8

"""CLI for Domain_Network project."""

import argparse
import json
from domain_network_utils import *
from tweet_reader import *
from url_processor import *
from network_generator import *
import pandas as pd



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

    # Domain network parameters
    parser.add_argument(
        "--url_shortener_list", "-u",
        nargs="+",
        type=str,
        help="list of shortener urls to be redirected"
    )
    parser.add_argument(
        "-nodes_list_to_remove", "-n",
        nargs="+",
        type=str,
        help="list of netlocs to be removed. E.g. social networks, shortener urls etc"
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

    # parser.add_argument('--dict_netlocs',
    #                     type=json.loads,
    #                     help = "dictionary keys = netlocs_to_replace and values= netlocs_to_remove")
    #File pathes to output
    parser.add_argument(
        "--network_only",
        type=bool,
        default=False,
        help="Read preprocessed file and make a network, instead of reading row tweet files and preprocess it"
    )
    parser.add_argument(
        "--urls_output_file_name",
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

    if args.network_only:
        #Read processed url file
        df_urls = read_dataframe(args.urls_output_file_name)
        print("df_urls: ",df_urls.shape)

    else:
        #Read tweets and preprocess it
        df_tweets_origin = read_tweets(args.input_dir)
        df_tweets = wide_to_long_url(df_tweets_origin)

        #Process URLs
        df_urls = process_urls(df_tweets, args.url_shortener_list, args.urls_output_file_name)

    domain_network = DomainNetwork(
        df_urls,
        args.nodes_list_to_remove,
        args.min_edge_weight,
        args.min_node_size,
        args.min_stand_alone_size,
        args.network_output_file_name,
        args.netloc_output_file_name,
        args.netloc_origin_output_file_name
    )

    # dict_change_netlocs = args.dict_netlocs
    dict_change_netlocs ={}
    dict_change_netlocs['ft.com'] = 'on.ft.com'
    dict_change_netlocs['ft.com'] = 'FT.com'
    dict_change_netlocs['bloom.bg'] = 'bloomberg.com'
    dict_change_netlocs['agweb.com'] = 'Agweb.com'
    dict_change_netlocs['reut.rs'] = 'reuters.com'

    dict_change_netlocs['reut.rs'] = 'feeds.reuters.com'
    dict_change_netlocs['forbes.com'] = 'onforb.es'
    dict_change_netlocs['sumof.us'] = 'actions.sumofus.org'
    dict_change_netlocs['wsj.com'] = 'on.wsj.com'
    dict_change_netlocs['reut.rs'] = 'uk.reuters.com'

    dict_change_netlocs['cnn.it'] = 'money.cnn.com'
    dict_change_netlocs['cnn.it'] = 'rss.cnn.com'
    dict_change_netlocs['bbc.com'] = 'bbc.co.uk'
    dict_change_netlocs['bbc.com'] = 'bbc.in'
    dict_change_netlocs['naturalnews.com'] = 'NaturalNews.com'

    dict_change_netlocs['act.wemove.eu'] = 'you.wemove.eu'
    dict_change_netlocs['act.wemove.eu'] = 'share.wemove.eu'
    dict_change_netlocs['act.credoaction.com'] = 'share.credoaction.com'
    dict_change_netlocs['nytimes.com'] = 'nyti.ms'
    dict_change_netlocs['credoaction.com'] = 'act.credoaction.com'

    dict_change_netlocs['wemove.eu'] = 'act.wemove.eu'
    dict_change_netlocs['sierraclub.org'] = 'act.sierraclub.org'
    dict_change_netlocs['nrdc.org'] = 'on.nrdc.org'
    dict_change_netlocs['avaaz.org'] = 'secure.avaaz.org'
    dict_change_netlocs['AltHealthWorks.com'] = 'althealthworks.com'

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