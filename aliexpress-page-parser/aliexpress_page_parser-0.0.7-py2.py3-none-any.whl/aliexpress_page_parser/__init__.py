# -*- coding: utf-8 -*-

# Copyright :copyright: 2019 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

import sys
import logging


logger = logging.getLogger('AliexpressPageParser.' + __name__)
formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
