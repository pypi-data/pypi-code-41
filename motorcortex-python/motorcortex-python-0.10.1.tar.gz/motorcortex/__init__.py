#!/usr/bin/python3

#
#   Developer : Alexey Zakharov (alexey.zakharov@vectioneer.com)
#   All rights reserved. Copyright (c) 2016 VECTIONEER.
#

from motorcortex.parameter_tree import ParameterTree
from motorcortex.message_types import MessageTypes
from motorcortex.request import Request
from motorcortex.reply import Reply
from motorcortex.subscribe import Subscribe
from motorcortex.subscription import Subscription
from motorcortex.motorcortex_pb2 import *

def statusToStr(motorcortex_msg, code):
    """Converts status codes to a readable message.

        Args:
            motorcortex_msg(Module): refernce to a motorcortex module
            code(int): status code

        Returns:
            str: status message

        Examples:
            >>> login_reply = req.login("admin", "iddqd")
            >>> login_reply_msg = login_reply.get()
            >>> if login_reply_msg.status != motorcortex_msg.OK:
            >>>     print(motorcortex.statusToStr(motorcortex_msg, login_reply_msg.status))

    """

    status = ''
    if code == motorcortex_msg.OK:
        status = 'Success'
    elif code == motorcortex_msg.FAILED:
        status = 'Failed'
    elif code == motorcortex_msg.FAILED_TO_DECODE:
        status = 'Failed to decode request'
    elif code == motorcortex_msg.SUB_LIST_IS_FULL:
        status = 'Failed to subscribe, subscription list is full'
    elif code == motorcortex_msg.WRONG_PARAMETER_PATH:
        status = 'Failed to find parameter'
    elif code == motorcortex_msg.FAILED_TO_SET_REQUESTED_FRQ:
        status = 'Failed to set requested frequency'
    elif code == motorcortex_msg.FAILED_TO_OPEN_FILE:
        status = 'Failed to open file'
    elif code == motorcortex_msg.READ_ONLY_MODE:
        status = 'Logged in, read-only mode'
    elif code == motorcortex_msg.WRONG_PASSWORD:
        status = 'Wrong login or password'
    elif code == motorcortex_msg.USER_NOT_LOGGED_IN:
        status = 'Operation is not permitted, user is not logged in'
    elif code == motorcortex_msg.PERMISSION_DENIED:
        status = 'Operation is not permitted, user has no rights'
    else:
        status = 'Unknown code'

    status += str(' (%s)' % hex(code))

    return status
