# coding=utf-8
from __future__ import absolute_import, print_function

import os

from suanpan.objects import Context

g = Context(
    userId=os.environ.get("SP_USER_ID"),
    appId=os.environ.get("SP_APP_ID"),
    nodeId=os.environ.get("SP_NODE_ID"),
    nodeGroup=os.environ.get("SP_NODE_GROUP", "default"),
)
