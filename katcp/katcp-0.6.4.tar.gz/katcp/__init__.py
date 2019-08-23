# __init__.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2009 SKA South Africa (http://ska.ac.za/)
# BSD license - see COPYING for details



"""Root of katcp package."""
from __future__ import division, print_function, absolute_import

from .core import (Message, KatcpSyntaxError, MessageParser,
                   DeviceMetaclass, FailReply,
                   AsyncReply, KatcpDeviceError, KatcpClientError,
                   Sensor, ProtocolFlags, AttrDict)

from .server import (DeviceServerBase, DeviceServer, AsyncDeviceServer,
                     DeviceLogger)

from .client import (DeviceClient, AsyncClient, CallbackClient,
                     BlockingClient)

from .resource_client import (KATCPClientResource, KATCPClientResourceContainer)

from .sensortree import (GenericSensorTree, BooleanSensorTree,
                         AggregateSensorTree)


# Automatically added by katversion
__version__ = '0.6.4'
