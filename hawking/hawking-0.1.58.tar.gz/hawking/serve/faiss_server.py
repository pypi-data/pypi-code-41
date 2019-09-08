""" Faiss Index Server.

"""
import os
import json
import logging
import time

import click
import faiss
import uuid
import grpc
import numpy as np

from concurrent import futures
from urllib.request import urlretrieve
from hawking_proto import hawking_pb2, hawking_pb2_grpc
from hawking.encoder import create_encoder
from google.cloud import storage
from hawking.serve.caption_server import CaptionServicer
from hawking.serve import configure_logging


_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def download_gcs_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print('Blob {} downloaded to {}.'.format(
        source_blob_name,
        destination_file_name))


class SearchServicer(hawking_pb2_grpc.SearchServicer):
    """ Implements hawking_pb2_grpc.SearchServicer. """

    def __init__(self, index_path, indexer_host, indexer_port, caption_host, caption_port, encoder_config):
        del indexer_host
        del indexer_port

        self.ready = False
        self.caption_stub = None
        self.caption_servicer = None

        if caption_host == '127.0.0.1':
            logging.info('Loading caption service ... {}:{}'.format(caption_host, caption_port))
            filename, ext = os.path.splitext(index_path)
            self.caption_servicer = CaptionServicer('{}.caption'.format(filename))
        else:
            logging.info('Connecting to caption service ... {}:{}'.format(caption_host, caption_port))
            self.channel = grpc.insecure_channel('{}:{}'.format(caption_host, caption_port))
            self.caption_stub = hawking_pb2_grpc.CaptionStub(self.channel)

        self.LoadIndex(index_path)
        logging.info(encoder_config)
        self.entity_type = encoder_config['entity_type']
        self.encoder = create_encoder(config=encoder_config)
        logging.info('Fx is ready to serve ...')
        self.ready = True

    def GetCaption(self, request):
        return (self.caption_stub.Get(request)
                if self.caption_stub is not None
                else self.caption_servicer.Get(request, None))

    def LoadIndex(self, index_path):
        assert os.path.exists(index_path), "Index {} does not exist!".format(index_path)
        logging.info('Loading index {}'.format(index_path))
        st = time.time()
        self.index = faiss.read_index(index_path)
        et = time.time() - st
        logging.info('Index loaded. Elapsed time: %.2f s' % et)

    def Get(self, request, context):
        """ Process text, image query.

        for image query, it supports and understands gs://, file:, http[s]:// prefix.
        """
        logging.info('Receive query: {}'.format(request))
        if not self.ready:
            raise Exception('Server is not ready to serve ...')
        query_response = hawking_pb2.SearchResponse()

        try:
            logging.info(self.entity_type)
            if request.type == hawking_pb2.SearchRequest.EntityType.IMAGE:
                image_uri = request.query
                if image_uri.startswith('file:'):
                    tmp_file = image_uri[len('file:'):]
                else:
                    tmp_file = '/tmp/' + str(uuid.uuid4())
                    logging.info('Downloading {} to {}'.format(image_uri, tmp_file))
                    if image_uri.startswith('http'):
                        urlretrieve(image_uri, tmp_file)
                    elif image_uri.startswith('gs://'):
                        tmp_uri = image_uri
                        tokens = tmp_uri[:6].split('/')
                        bucket_name = tokens[0]
                        source_uri = '/'.join(tokens[:1])
                        download_gcs_blob(bucket_name, source_uri, tmp_file)
                # TODO(oleg): do base64 format.
                vector = self.encoder.encode(tmp_file, flattened=False)
            elif request.type == hawking_pb2.SearchRequest.EntityType.TEXT:
                vector = self.encoder.encode(request.query)
            else:
                raise ValueError('Query for entity type {} is not supported.'.format(
                    request.type))
            np.set_printoptions(threshold=5)
            logging.info('Obtained {} vector({}): {}'.format(request.query, vector.shape, vector))
            logging.info('Querying index...')
            D, I = self.index.search(vector, request.max_results)

            # Retrieve captions from caption_server, for image type it returns image uri,
            # for text, it will return metadata.
            logging.info('Querying caption...')
            caption_request = hawking_pb2.SnippetRequest(max_length=250, prettify=False)
            for doc_id in I[0]:
                caption_request.doc_ids.append(doc_id)

            st = time.time()
            caption_response = self.GetCaption(caption_request)

            logging.info('Search results:')
            for snippet, doc_id, score in zip(caption_response.snippets, I[0], D[0]):
                query_response.results.append(
                    hawking_pb2.Result(
                        score=score,
                        document=hawking_pb2.Document(uuid=str(doc_id), body=snippet.title)))

            et = (time.time() - st) * 1000.0
            logging.info('elapsed time: %d ms' % et)
            logging.info('Response:{}'.format(query_response))
        except Exception as e:
            logging.error(e)
        return query_response


def serve(index_path, indexer_host, indexer_port, caption_host, caption_port, worker_threads, grpc_port,
          encoder_config, run_bot):
    configure_logging()

    logging.info('TAG: FX')
    logging.info('Starting gRPC index server ...')
    logging.info(encoder_config)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=worker_threads))
    search_servicer = SearchServicer(
        index_path,
        indexer_host, indexer_port,
        caption_host, caption_port,
        encoder_config)
    hawking_pb2_grpc.add_SearchServicer_to_server(search_servicer, server)
    server.add_insecure_port('[::]:{}'.format(grpc_port))
    server.start()
    #
    # from hawking.bot.secretary import serve as start_secretary
    # from hawking.bot.telegram import serve as start_bot
    # bot = None
    # secretary = None
    # if run_bot:
    #     bot = start_bot(bot_token='701884073:AAF9rkmy73sq6U3QPbZxX5JzyfkDqhP-5xQ')
    #     # TODO(oleg): add secretary bot token.
    #     secretary = None

    logging.info('Ready to serve. Listening on 0.0.0.0:{}'.format(grpc_port))
    logging.info('Press Ctrl+C to exit ...')


    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        # if bot is not None:
        #    bot.stop()
        # if secretary is not None:
        #    secretary.stop()
        if server is not None:
            server.stop(0)


@click.command()
@click.option('--index-path', help="Index path.", default=None)
@click.option('--indexer-host', help="Indexer backend host url/ip.", default='127.0.0.1')
@click.option('--indexer-port', help="Indexer backend host port.", default=5000)
@click.option('--caption-host', help="Caption server host url/ip.", default='127.0.0.1')
@click.option('--caption-port', help="Caption server port.", default=50001)
@click.option('--worker-threads', '-w', help="Maximum numbers of worker threads.", default=10)
@click.option('--grpc-port', help="gRPC port to listen to request.", default=50000)
@click.option('--encoder-config', help="Encoder pre-trained weights.", default='/tmp/encoder_config.json')
@click.option('--run-bot/--no-run-bot', help="Run telegram bot.", default=False)
def run(index_path, indexer_host, indexer_port, caption_host, caption_port, worker_threads,
        grpc_port, encoder_config, run_bot):
    """Run server
    example of encoder_config:
    {
        'entity_type': 'text',
        'encoder_type': 'universal-sentence-encoder',
        'weights': 'https://tfhub.dev/google/universal-sentence-encoder-multilingual-qa/1',
        'encoder_host': '127.0.0.1',
        'encoder_port': 5555,
        'top_layer': "fc1000",
        'print_summary': False,
    }
    """
    with open(encoder_config, 'r') as f:
        encoder_config = json.load(f)
    serve(index_path,
          indexer_host, int(indexer_port),
          caption_host, int(caption_port),
          int(worker_threads), int(grpc_port), encoder_config, run_bot)


if __name__ == "__main__":
    run()
