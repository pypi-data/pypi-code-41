""" Queue Server.

"""
import os
import json
import logging
import sqlite3
import sys
import time
import threading

import click
import grpc

from concurrent import futures
from hawking_proto import hawking_pb2, hawking_pb2_grpc
from hawking.encoder.bert import BertTextEncoder


_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class QueueServicer(hawking_pb2_grpc.QueueServicer, hawking_pb2_grpc.IndexServicer):
    """ Implements hawking_pb2_grpc.QueueServicer. """

    def __init__(self, queue_path):
        self.db_file = os.path.join(queue_path, "queue.db")
        logging.info("Use {} file".format(self.db_file))

        connection = sqlite3.connect(self.db_file)
        try:
            connection.execute("CREATE TABLE IF NOT EXISTS queue (checkpoint INTEGER PRIMARY KEY, namespace VARCHAR(1024), document JSON NOT NULL);")
            connection.commit()
        finally:
            connection.close()

        self.condition = threading.Condition()


    def _poll(self, checkpoint):
        connection = sqlite3.connect(self.db_file)
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT namespace, document FROM queue WHERE checkpoint = ?", (checkpoint,) )

            row = cursor.fetchone()
            if row is None:
                return None

            return {"namespace": row[0], "document": row[1] }
        finally:
            connection.close()

    def Poll(self, request, context):
        """
            option (google.api.http) = {
                post: "/v1/post"
                body: "*"
            };
        """
        checkpoint = 1 if request.checkpoint is None or request.checkpoint == '' else (int(request.checkpoint))
        logging.info("{} start with checkpoint {}".format(context.peer(), checkpoint))

        while True:
            response = None
            self.condition.acquire()

            item = self._poll(checkpoint)
            while item is None:
                self.condition.wait()
                item = self._poll(checkpoint)

            checkpoint += 1

            namespace = item['namespace']
            record = json.loads(item['document'])
            response = hawking_pb2.PollResponse(checkpoint = str(checkpoint),
                                                namespace = namespace,
                                                document = hawking_pb2.Document(uuid=record['uuid'], body=record['content']))

            self.condition.release()
            yield response


        


    """ Implements hawking_pb2_grpc.IndexServicer. """

    def Post(self, request, context):
        """
            option (google.api.http) = {
                post: "/v1/post"
                body: "*"
            };
        """
        self.condition.acquire()

        connection = sqlite3.connect(self.db_file)
        try:
            for document in request.documents:
                logging.info('Enqueue "{}/{}/{}"'.format(request.namespace, document.uuid, document.body))
                connection.execute("INSERT INTO queue (namespace, document) VALUES (?, ?)",
                    (request.namespace, json.dumps({"uuid":document.uuid, "content": document.body}))
                )

            connection.commit()
        finally:
            connection.close()

        self.condition.notifyAll()
        self.condition.release()

        return hawking_pb2.IndexResponse(inserted=True)



def serve(queue_path, worker_threads, grpc_port):
    logging.info('TAG: Queue')
    logging.info('Starting gRPC queue server ...')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=worker_threads))
    queue_servicer = QueueServicer(queue_path)
    hawking_pb2_grpc.add_QueueServicer_to_server(queue_servicer, server)
    hawking_pb2_grpc.add_IndexServicer_to_server(queue_servicer, server)
    server.add_insecure_port('[::]:{}'.format(grpc_port))
    server.start()

    logging.info('Ready to serve. Listening on 0.0.0.0:{}'.format(grpc_port))
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


@click.command()
@click.option('--queue-path', help="Queue dir for stuff.", default="/tmp")
@click.option('--worker-threads', '-w', help="Maximum numbers of worker threads.", default=10)
@click.option('--grpc-port', help="gRPC port to listen to request.", default=45000)
def run(queue_path, worker_threads, grpc_port):
    serve(queue_path, int(worker_threads), int(grpc_port))


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    run()
