#!/usr/bin/python3

#
#   Developer : Alexey Zakharov (alexey.zakharov@vectioneer.com)
#   All rights reserved. Copyright (c) 2016 VECTIONEER.
#

from motorcortex.reply import Reply

from concurrent.futures import ThreadPoolExecutor
from nanomsg import wrapper as nn
from nanomsg import REQ, SOL_SOCKET, RCVTIMEO, RCVMAXSIZE, AF_SP, create_writable_buffer
from builtins import bytes

class Request(object):
    """Request/Reply communication is used to send commands to a motorcortex server.

        Args:
            protobuf_types(MessageTypes): reference to a MessageTypes instance
            parameter_tree(ParameterTree): reference to a ParameterTree instance
    """

    def __init__(self, protobuf_types, parameter_tree):
        self.__protobuf_types = protobuf_types
        self.__parameter_tree = parameter_tree
        self.__socket = None
        self.__pool = ThreadPoolExecutor(1)

    def connect(self, url, timeout_ms=0):
        """Opens a request connection.

            Args:
                url(str): motorcortex server URL
                timeout_ms(int): request timeout in milliseconds

            Returns:
                bool: True - if connected, False otherwise

        """

        socket = nn.nn_socket(AF_SP, REQ)

        # setting receive buffer size to inf
        recv_size = bytes([0xff, 0xff, 0xff, 0xff])
        nn.nn_setsockopt(socket, SOL_SOCKET, RCVMAXSIZE, recv_size)

        if timeout_ms > 0:
            timeout_buf = bytes(
                [timeout_ms & 0xff, (timeout_ms >> 8) & 0xff, (timeout_ms >> 16) & 0xff, (timeout_ms >> 24) & 0xff])
            nn.nn_setsockopt(socket, SOL_SOCKET, RCVTIMEO, timeout_buf)

        if (nn.nn_connect(socket, url) == 1):
            self.__socket = socket
            return True

        return False

    def close(self):
        """Closes connection to the server"""

        nn.nn_close(self.__socket)
        self.__socket = None
        print("Reply connection closed")

    def __send(self, encoded_msg, do_not_decode_reply):
        socket = self.__socket
        nn.nn_send(socket, encoded_msg, 0)
        length, buffer = nn.nn_recv(socket, 0)
        if length > 0:
            if do_not_decode_reply:
                return buffer
            else:
                return self.__protobuf_types.decode(bytes(buffer))

        return None

    def send(self, encoded_msg, do_not_decode_reply=False):
        """Sends an encoded request to the server

            Args:
                encoded_msg(list(bytes)): binary array with encoded message
                do_not_decode_reply(bool): if True reply is returned as a binary buffer

            Returns:
                Reply: A promise, which completes when reply from the server is received.
                If request fails, catch callback is triggered.

            Examples:
                >>> msg = motorcortex.createType('motorcortex.LoadMsg')
                >>> msg.file_name = 'control.xml'
                >>> reply = req.send(req.encode(msg))
                >>> reply_value = reply.get()
        """

        if self.__socket is not None:
            return Reply(self.__pool.submit(self.__send, encoded_msg, do_not_decode_reply))

        return None

    def login(self, login, password):
        """Sends a login request to the server

            Args:
                login(str): user login
                password(str): user password

            Results:
                Reply(StatusMsg): A Promise, which resolves if login is successful and fails otherwise.
                Returned message has a status code, which indicates a status of the login.

            Examples:
                >>> login_reply = req.login('operator', 'god123');
                >>> login_msg = login_reply.get()
                >>> if login_msg.status == motorcortex_msg.OK
                >>>     print('User logged-in')

        """

        login_msg = self.__protobuf_types.createType('motorcortex.LoginMsg')
        login_msg.password = password
        login_msg.login = login

        return self.send(self.__protobuf_types.encode(login_msg))

    def getParameterTree(self):
        """Requests a parameter tree from the server.

            Returns:
                Reply(ParameterTreeMsg): A Promise, which resolves when parameter tree is received or fails
                otherwise. ParameterTreeMsg message has a status files to check the status of the operation.

            Examples:
                >>> param_tree_reply = req.getParameterTree()
                >>> value = param_tree_reply.get()
                >>> parameter_tree.load(value)

        """

        # getting and instantiating data type from the loaded dict
        param_tree_msg = self.__protobuf_types.createType('motorcortex.GetParameterTreeMsg')

        # encoding and sending data
        return self.send(self.__protobuf_types.encode(param_tree_msg))

    def save(self, path, file_name):
        """Request a server to save a parameter tree to file.

            Args:
                path(str): path where to save
                file_name(str): file name

            Returns:
                Reply(StatusMsg): A promise, which resolves when save operation is completed,
                fails otherwise.

        """

        param_save_msg = self.__protobuf_types.createType('motorcortex.SaveMsg')
        param_save_msg.path = path;
        param_save_msg.file_name = file_name;

        return self.send(self.__protobuf_types.encode(param_save_msg))

    def setParameter(self, path, value, type_name=None):
        """Sets new value to a parameter with given path

            Args:
                path(str): parameter path in the tree
                value(any): new parameter value
                type_name(str): type of the value (by default resolved automatically)

            Returns:
                  Reply(StatusMsg): A Promise, which resolves when parameter value is updated or fails otherwise.

            Examples:
                  >>> reply = req.setParameter("root/Control/activateSemiAuto", False);
                  >>> reply.get();
                  >>> reply = req.setParameter("root/Control/targetJointAngles", [0.2, 3.14, 0.4]);
                  >>> reply.get()
        """

        return self.send(self.__protobuf_types.encode(self.__buildSetParameterMsg(path, value, type_name)))

    def setParameterList(self, param_list):
        """Sets new values to a parameter list

            Args:
                 param_list([{'path'-`str`,'value'-`any`}]): a list of the parameters which values update

            Returns:
                Reply(StatusMsg): A Promise, which resolves when parameters from the list are updated,
                otherwise fails.

            Examples:
                  >>>  req.setParameterList([
                  >>>   {'path': 'root/Control/generator/enable', 'value': False},
                  >>>   {'path': 'root/Control/generator/amplitude', 'value': 1.4}])

        """

        # instantiating message type
        set_param_list_msg = self.__protobuf_types.createType("motorcortex.SetParameterListMsg")
        # filling with sub messages
        for param in param_list:
            type_name = None
            if "type_name" in param:
                type_name = param["type_name"]
            set_param_list_msg.params.extend([self.__buildSetParameterMsg(param["path"], param["value"], type_name)])

        # encoding and sending data
        return self.send(self.__protobuf_types.encode(set_param_list_msg))

    def getParameter(self, path):
        """Requests a parameter with description and value from the server.

            Args:
                path_list(str): parameter path in the tree.

            Returns:
                 Reply(ParameterMsg): Returns a Promise, which resolves when parameter
                 message is successfully obtained, fails otherwise.

            Examples:
                >>> param_reply = req.getParameter('root/Control/actualActuatorPositions')
                >>> param_full = param_reply.get() # Value and description
        """

        return self.send(self.__protobuf_types.encode(self.__buildGetParameterMsg(path)))

    def getParameterList(self, path_list):
        """Get description and values of requested parameters.

            Args:
                path_list(str): list of parameter paths in the tree.

            Returns:
                Reply(ParameterListMsg): A Promise, which resolves when list of the parameter values is received, fails
                otherwise.

            Examples:
                >>> params_reply = req.getParameter(['root/Control/joint1', 'root/Control/joint2'])
                >>> params_full = params_reply.get() # Values and descriptions
                >>> print(params_full.params)
        """

        # instantiating message type
        get_param_list_msg = self.__protobuf_types.createType('motorcortex.GetParameterListMsg')
        # filling with sub messages
        for path in path_list:
            get_param_list_msg.params.extend([self.__buildGetParameterMsg(path)])

        # encoding and sending data
        return self.send(self.__protobuf_types.encode(get_param_list_msg))

    def createGroup(self, path_list, group_alias, frq_divider=1):
        """Creates a subscription group for a list of the parameters.

            This method is used inside Subscription class, use subscription class instead.

            Args:
                path_list(list(str)): list of the parameters to subscribe to
                group_alias(str): name of the group
                frq_divider(int): frequency divider is a downscaling factor for the group publish rate

            Returns:
                Reply(GroupStatusMsg): A Promise, which resolves when subscription is complete,
                fails otherwise.
        """

        # instantiating message type
        create_group_msg = self.__protobuf_types.createType('motorcortex.CreateGroupMsg')
        create_group_msg.alias = group_alias
        create_group_msg.paths.extend(path_list if type(path_list) is list else [path_list])
        create_group_msg.frq_divider = frq_divider if frq_divider > 1 else 1
        # encoding and sending data
        return self.send(self.__protobuf_types.encode(create_group_msg))

    def removeGroup(self, group_alias):
        """Unsubscribes from the group.

            This method is used inside Subscription class, use subscription class instead.

            Args:
                group_alias(str): name of the group to unsubscribe from

            Returns:
                Reply(StatusMsg): A Promise, which resolves when the unsubscribe operation is complete,
                fails otherwise.
        """

        # instantiating message type
        remove_group_msg = self.__protobuf_types.createType('motorcortex.RemoveGroupMsg')
        remove_group_msg.alias = group_alias
        # encoding and sending data
        return self.send(self.__protobuf_types.encode(remove_group_msg));

    def __buildSetParameterMsg(self, path, value, type_name):
        param_value = None
        if not type_name:
            type_id = self.__parameter_tree.getDataType(path)
            if type_id:
                param_value = self.__protobuf_types.getTypeByHash(type_id)
        else:
            param_value = self.__protobuf_types.createType(type_name)

        if not param_value:
            print("Failed to find encoder for the path: %s type: %s" % (path, type_name))

        # creating type instance
        set_param_msg = self.__protobuf_types.createType("motorcortex.SetParameterMsg")
        set_param_msg.path = path
        # encoding parameter value
        set_param_msg.value = param_value.encode(value)

        return set_param_msg

    def __buildGetParameterMsg(self, path):
        # getting and instantiating data type from the loaded dict
        get_param_msg = self.__protobuf_types.createType('motorcortex.GetParameterMsg')
        get_param_msg.path = path

        return get_param_msg
