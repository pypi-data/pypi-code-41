""" Node Server.

"""
import os
import logging
import sys

import time
import threading

import click
import grpc
import sqlite3

from concurrent import futures
from hawking_proto import hawking_pb2, hawking_pb2_grpc



_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class StoreServicer(hawking_pb2_grpc.StoreServicer):
    """ Implements hawking_pb2_grpc.StoreServicer. """

    def __init__(self, store_path):
        self.namespaces = {}
        self.db_file = os.path.join(store_path, "store.db")
        logging.info("Use {} file".format(self.db_file))
        connection = sqlite3.connect(self.db_file)
        try:
            connection.execute("CREATE TABLE IF NOT EXISTS data (namespace VARCHAR(1024), uuid VARCHAR(1024), content JSON NOT NULL, PRIMARY KEY (namespace, uuid));")
            connection.commit()
        finally:
            connection.close()

    def Put(self, request, context):
        connection = sqlite3.connect(self.db_file)
        try:
            connection.execute("INSERT OR REPLACE INTO data (namespace, uuid, content) VALUES (?, ?, ?)",
                (request.namespace, request.document.uuid, request.document.body)
            )
            connection.commit()
        finally:
            connection.close()

        logging.info("Store {}/{}: {}".format(request.namespace, request.document.uuid, request.document.body))
        return hawking_pb2.StorePutResponse(uuid=request.document.uuid)


    def Get(self, request, context):
        connection = sqlite3.connect(self.db_file)
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT content FROM data WHERE namespace = ? AND uuid = ?",
                (request.namespace, request.uuid)
            )

            row = cursor.fetchone()
            if row is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Object `" + request.namespace + "/" + request.uuid + "` not found!")
                raise ValueError("Object `" + request.namespace + "/" + request.uuid + "` not found!")

            content = row[0]
            logging.info("Retrieve {}/{}: {}".format(request.namespace, request.uuid, content))
            return hawking_pb2.StoreGetResponse(document=
                hawking_pb2.Document(body=content, uuid=request.uuid))
        finally:
            connection.close()


def serve(store_path, worker_threads, grpc_port):
    logging.info('TAG: Store')
    logging.info('Starting gRPC queue server ...')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=worker_threads))
    queue_servicer = StoreServicer(store_path)
    hawking_pb2_grpc.add_StoreServicer_to_server(queue_servicer, server)
    server.add_insecure_port('[::]:{}'.format(grpc_port))
    server.start()

    logging.info('Ready to serve. Listening on 0.0.0.0:{}'.format(grpc_port))
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


@click.command()
@click.option('--store-path', help="Store dir for stuff.", default="/tmp")
@click.option('--worker-threads', '-w', help="Maximum numbers of worker threads.", default=10)
@click.option('--grpc-port', help="gRPC port to listen to request.", default=42000)
def run(store_path, worker_threads, grpc_port):
    serve(store_path, int(worker_threads), int(grpc_port))


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    run()
