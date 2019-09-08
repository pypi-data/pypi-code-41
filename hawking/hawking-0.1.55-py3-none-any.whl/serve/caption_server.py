""" Faiss Index Server.

"""
import os
import logging
import time

import click
import grpc

from concurrent import futures
from hawking_proto import hawking_pb2, hawking_pb2_grpc
from hawking.serve import configure_logging


_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class CaptionServicer(hawking_pb2_grpc.CaptionServicer):
    """ Implements hawking_pb2_grpc.CaptionServicer. """

    def __init__(self, index_path):
        self.LoadIndex(index_path)

    def LoadIndex(self, index_path):
        """ Load forward index. """
        assert os.path.exists(index_path), "Index {} does not exist!".format(index_path)
        logging.info('Loading index {}'.format(index_path))
        st = time.time()
        self.forward_index = []
        with open(index_path, 'r') as f:
            for line in f:
                line = line.strip()
                tokens = line.split('\t')
                assert len(tokens) == 1
                title = tokens[0]
                body = None
                if len(tokens) > 1:
                    body = tokens[1]
                meta = None
                if len(tokens) > 2:
                    meta = tokens[2]
                self.forward_index.append((title, body, meta))
        self.total_docs = len(self.forward_index)
        et = time.time() - st
        logging.info('Index loaded. Elapsed time: %.2f s' % et)

    def Get(self, request, context):
        logging.info('Receive query: {}'.format(request))

        response = hawking_pb2.SnippetResponse()
        for doc_id in request.doc_ids:
            title, body, meta = ('', '', '')
            if doc_id < self.total_docs:
                snippet = self.forward_index[doc_id]
                title, body, meta = snippet
            response.snippets.append(hawking_pb2.Snippet(title=title, body=body, metadata=meta))
        logging.info('Response:{}'.format(response))
        return response


def serve(index_path, worker_threads, grpc_port):
    configure_logging()

    logging.info('TAG: CAPTION')
    logging.info('Starting gRPC index server ...')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=worker_threads))
    caption_servicer = CaptionServicer(index_path)
    hawking_pb2_grpc.add_CaptionServicer_to_server(caption_servicer, server)
    server.add_insecure_port('[::]:{}'.format(grpc_port))
    server.start()
    logging.info('Ready to serve. Listening on 0.0.0.0:{}'.format(grpc_port))
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


@click.command()
@click.option('--index-path', help="Index path.", default=None)
@click.option('--worker-threads', '-w', help="Maximum numbers of worker threads.", default=10)
@click.option('--grpc-port', help="gRPC port to listen to request.", default=50001)
def run(index_path, worker_threads, grpc_port):
    serve(index_path, int(worker_threads), int(grpc_port))


if __name__ == "__main__":
    run()
