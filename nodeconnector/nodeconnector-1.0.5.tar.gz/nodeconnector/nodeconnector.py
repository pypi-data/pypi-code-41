""" 
Python connector module for Node.JS applications

"""
__version__ = '1.0.5'

import json
import zmq
import threading


class Interface(threading.Thread):
    # create
    def __init__(self):
        self.port = 24001
        self.socket_address = 'tcp://127.0.0.1:%d' % self.port

        # publisher socket
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)

        # routes
        self.router = {}

        # thread processing
        threading.Thread.__init__(self)
        self.setDaemon(True)

    # task processing
    def run(self):
        # infinite loop
        while(True):
            # query processing
            query = json.loads(self.socket.recv_string())

            # return registered handlers
            if(query['_p'] == '__pyroutes'):
                reply = [k for k in self.router]
                self.socket.send_json(
                    dict(_p=query['_p'], _id=query['_id'], data=reply))

            # check query path
            elif(query['_p'] in self.router):
                fn, ctx = self.router[query['_p']]
                args = {}
                if('args' in query):
                    args = query['args']

                # execute handler
                reply = fn(args, ctx)

                self.socket.send_json(
                    dict(_p=query['_p'], _id=query['_id'], data=reply))

    # routing queries

    def handle(self, path, handle, context={}):
        self.router[path] = (handle, context)

    # launch interface
    def listen(self, port=24001):
        self.port = int(port)
        self.socket_address = 'tcp://127.0.0.1:%d' % self.port
        self.socket.bind(self.socket_address)

        self.start()
