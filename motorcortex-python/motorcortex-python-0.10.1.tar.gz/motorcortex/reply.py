#!/usr/bin/python3

#
#   Developer : Alexey Zakharov (alexey.zakharov@vectioneer.com)
#   All rights reserved. Copyright (c) 2016 VECTIONEER.
#

class Reply(object):
    """Reply handle is a JavaScript-like Promise.

        It is resolved when reply is received with successful status and fails otherwise.
    """

    def __init__(self, future):
        self.__future = future

    def get(self, timeout=None):
        """A blocking call to wait for the reply and returns a value.

            Args:
                timeout(float): timeout for reply in seconds

            Returns:
                A protobuf message with a parameter description and value.

            Examples:
                  >>> param_tree_reply = req.getParameterTree()
                  >>> value = param_tree_reply.get()

        """
        return self.__future.result(timeout)

    def done(self):
        """
            Returns:
                bool: True if the call was successfully cancelled or finished running.
        """
        return self.__future.done()

    def then(self, received_clb):
        """JavaScript-like promise, which is resolved when reply is received.

                Args:
                    received_clb: callback which is resolved when reply is received.

                Returns:
                    self pointer to add 'catch' callback

                Examples:
                    >>> param_tree_reply.then(lambda reply: print("got reply: %s"%reply)).catch(lambda g: print("failed"))
        """
        self.__future.add_done_callback(
            lambda msg: received_clb(msg.result()) if msg.result() else None
        )
        return self

    def catch(self, failed_clb):
        """JavaScript-like promise, which is resolved when receive has failed.

            Args:
                failed_clb: callback which is resolved when receive has failed

            Returns:
                self pointer to add 'then' callback

            Examples:
                >>> param_tree_reply.catch(lambda g: print("failed")).then(lambda reply: print("got reply: %s"%reply))
        """
        self.__future.add_done_callback(
            lambda msg: failed_clb() if not msg.result() else None
        )
        return self
