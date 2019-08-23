#!/usr/bin/python3

#
#   Developer : Alexey Zakharov (alexey.zakharov@vectioneer.com)
#   All rights reserved. Copyright (c) 2016 VECTIONEER.
#


from motorcortex.subscription import Subscription
from builtins import bytes
import threading
from nanomsg import wrapper as nn
from nanomsg import SUB, SOL_SOCKET, RCVTIMEO, AF_SP, SUB_SUBSCRIBE, SUB_UNSUBSCRIBE, RCVBUF


class Subscribe(threading.Thread):
    """Subscribe class is used to receive continuous parameter updates from motorcortex server.
    
        Subscribe class simplifies creating and removing subscription groups.

        Args:
            req(Request): reference to a Request instance
            protobuf_types(MessageTypes): reference to a MessageTypes instance

    """

    def __init__(self, req, protobuf_types):
        threading.Thread.__init__(self)
        self.__req = req
        self.__protobuf_types = protobuf_types
        self.__socket = None
        self.__stop = threading.Event()
        self.__subscriptions = dict()

    def connect(self, url):
        """Opens a subscribe connection.

            Args:
                url(str): motorcortex server URL

            Returns:
                bool: True - if connected, False otherwise
        """

        socket = nn.nn_socket(AF_SP, SUB)
        if nn.nn_connect(socket, url) == 1:
            self.__socket = socket
            self.start()
            return True

        return False

    def close(self):
        """Closes connection to the server"""
        self.__stop.set()
        for id in list(self.__subscriptions):
            self.__unsubscribe(id)

        nn.nn_close(self.__socket)
        self.join()

    def run(self):
        while not self.__stop.is_set():
            length, buffer = nn.nn_recv(self.__socket, 0)
            if (length > 0):
                id_buf = bytes(buffer)[:4]
                # id = id_buf[0] + (id_buf[1] << 8) + (id_buf[2] << 16) + (id_buf[3] << 24)
                protocol_version = id_buf[3];
                id = id_buf[0] + (id_buf[1] << 8) + (id_buf[2] << 16)
                sub = self.__subscriptions.get(id)
                if sub:
                    if protocol_version == 1:
                        sub._updateProtocol1(bytes(buffer)[4:], length - 4)
                    elif protocol_version == 0:
                        sub._updateProtocol0(bytes(buffer)[4:], length - 4)
                    else:
                        print('Unknown protocol type: %d', protocol_version)

        print('Subscribe connection closed')

    def __complete(self, msg, subscription):
        if subscription._complete(msg):
            # id_buf = bytes([msg.id & 0xff, (msg.id >> 8) & 0xff, (msg.id >> 16) & 0xff, (msg.id >> 24) & 0xff])
            id_buf = bytes([msg.id & 0xff, (msg.id >> 8) & 0xff, (msg.id >> 16) & 0xff])
            nn.nn_setsockopt(self.__socket, SUB, SUB_SUBSCRIBE, id_buf)
            self.__subscriptions[msg.id] = subscription

    def subscribe(self, param_list, group_alias, frq_divider=1):
        """Create a subscription group for a list of the parameters.

            Args:
                param_list(list(str)): list of the parameters to subscribe to
                group_alias(str): name of the group
                frq_divider(int): frequency divider is a downscaling factor for the group publish rate

            Returns:
                  Subscription: A subscription handle, which acts as a JavaScript Promise,
                  it is resolved when subscription is ready or failed. After the subscription
                  is ready the handle is used to retrieve latest data.
        """

        subscription = Subscription(group_alias, self.__protobuf_types)
        reply = self.__req.createGroup(param_list, group_alias, frq_divider)
        reply.then(lambda msg, subscription=subscription: self.__complete(msg, subscription)).catch(
            subscription._failed)

        return subscription;

    def unsubscribe(self, subscription):
        """Unsubscribes from the group.

            Args:
                subscription(Subscription): subscription handle

            Returns:
                  Reply: Returns a Promise, which resolves when the unsubscribe
                  operation is complete, fails otherwise.

        """

        return self.__unsubscribe(subscription.id())

    def __unsubscribe(self, id):

        # id_buf = bytes([id & 0xff, (id >> 8) & 0xff, (id >> 16) & 0xff, (id >> 24) & 0xff])
        id_buf = bytes([id & 0xff, (id >> 8) & 0xff, (id >> 16) & 0xff])
        nn.nn_setsockopt(self.__socket, SUB, SUB_UNSUBSCRIBE, id_buf)

        sub = self.__subscriptions[id]
        # send remove group request to the server
        reply = self.__req.removeGroup(sub.alias())
        # stop sub update thread
        sub.done()

        del self.__subscriptions[id]

        return reply
