""" Faiss Index Server.

"""
import os
import logging
import sys
import time

import click
import grpc
import numpy as np

from concurrent import futures
from hawking_proto import hawking_pb2, hawking_pb2_grpc
from hawking.encoder.bert import BertTextEncoder
from hawking.sptag import SPTAGClient


_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class SearchServicer(hawking_pb2_grpc.SearchServicer):
    """ Implements hawking_pb2_grpc.SearchServicer. """

    def __init__(self, index_path, indexer_host, indexer_port, encoder_host, encoder_port):
        self.LoadIndex(index_path)
        logging.info('Connecting to text encoder service `{}:{}`...'.format(encoder_host, encoder_port))
        self.encoder = BertTextEncoder(encoder_host, encoder_port)
        logging.info('Successfully connected to text encoder service')

        logging.info('Connecting to indexer backend `{}:{}` ...'.format(indexer_host, indexer_port))
        self.sptag_client = SPTAGClient.AnnClient(indexer_host, str(indexer_port))
        while not self.sptag_client.IsConnected():
            logging.info('Connecting ...')
            time.sleep(1)
        logging.info('Successfully connected to indexer backend ...')

    def LoadIndex(self, index_path):
        pass

    def Get(self, request, context):
        logging.info('Receive query: {}'.format(request))
        st = time.time()
        vector = self.encoder.encode(request.query)
        result = self.sptag_client.Search(vector, request.max_results, 'Float', True)
        response = hawking_pb2.SearchResponse()
        for docid, dist, meta in zip(result[0], result[1], result[2]):
            response.results.append(
                    hawking_pb2.Result(
                        score=dist,
                        document=hawking_pb2.Document(uuid=str(docid), body=meta, parent=str(docid))))
        et = time.time() - st
        logging.info('Elapsed time: %d ms' % (et * 1000))
        return response


def serve(index_path, indexer_host, indexer_port, encoder_host, encoder_port, worker_threads, grpc_port):
    logging.info('TAG: SX')
    logging.info('Starting gRPC index server ...')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=worker_threads))
    search_servicer = SearchServicer(index_path, indexer_host, indexer_port, encoder_host, encoder_port)
    hawking_pb2_grpc.add_SearchServicer_to_server(search_servicer, server)
    server.add_insecure_port('[::]:{}'.format(grpc_port))
    server.start()
    logging.info('Ready to serve. Listening on 0.0.0.0:{}'.format(grpc_port))
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


@click.command()
@click.option('--index-path', '-idx', help="Index path.", default=None)
@click.option('--indexer-host', help="Indexer backend host url/ip.", default='127.0.0.1')
@click.option('--indexer-port', help="Indexer backend host port.", default=5000)
@click.option('--encoder-host', help="Remote text encoder host url/ip.", default='127.0.0.1')
@click.option('--encoder-port', help="Remote text encoder host port.", default=5555)
@click.option('--worker-threads', '-w', help="Maximum numbers of worker threads.", default=10)
@click.option('--grpc-port', help="gRPC port to listen to request.", default=50000)
def run(index_path, indexer_host, indexer_port, encoder_host, encoder_port, worker_threads, grpc_port):
    serve(index_path, indexer_host, indexer_port, encoder_host, encoder_port, int(worker_threads), grpc_port)


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    run()
