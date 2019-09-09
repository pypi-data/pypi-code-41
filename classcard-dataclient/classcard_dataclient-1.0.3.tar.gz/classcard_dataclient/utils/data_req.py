# -*- coding: utf-8 -*-
"""
Created By Murray(m18527) on 2019/9/4 17:18
"""
import os

from .requestutils import (do_get_request, do_post_request)
from .loggerutils import logging
from .constants import *

logger = logging.getLogger(__name__)


def class_card_server_url():
    """class_card server url"""
    server_url = os.getenv(CLASS_CARD_SERVER_URL_ENV, CLASS_CARD_SERVER_URL_DEFAULT)
    return server_url


def class_card_server_token():
    """class_card server token"""
    token = os.getenv(CLASS_CARD_SERVER_TOKEN_ENV, CLASS_CARD_SERVER_TOKEN_DEFAULT)
    return token


def get_device_info(school_id, sn):
    """get class device info by school_id and sn"""
    url = "{}/api/volcano/class_device/{}/".format(class_card_server_url(), sn)
    resp = do_get_request(url=url, token=class_card_server_token(), school_in_header=school_id)
    code = resp.code
    data = resp.data.get('data', {}) if not code else resp.msg
    if code:
        logger.error("Error: Request: {}, Detail: {}".format(url, data))
    return code, data


def get_school_info(school_id):
    """get school info by school_id"""
    url = "{}/api/school/{}/".format(class_card_server_url(), school_id)
    resp = do_get_request(url=url, token=class_card_server_token(), school_in_header=school_id)
    code = resp.code
    data = resp.data.get('data', {}) if not code else resp.msg
    if code:
        logger.error("Error: Request: {}, Detail: {}".format(url, data))
    return code, data


def create_section_req(data, school_id):
    """create section of class card server"""
    url = "{}/api/class/".format(class_card_server_url())
    resp = do_post_request(url=url, json=data, token=class_card_server_token(), school_in_header=school_id)
    code = resp.code
    data = resp.data.get('data', {}) if not code else resp.msg
    if code:
        logger.error("Error: Request: {}, Detail: {}".format(url, data))
    return code, data


def create_classroom_req(data, school_id):
    """create classroom of class card server"""
    url = "{}/api/classroom/".format(class_card_server_url())
    resp = do_post_request(url=url, json=data, token=class_card_server_token(), school_in_header=school_id)
    code = resp.code
    data = resp.data.get('data', {}) if not code else resp.msg
    if code:
        logger.error("Error: Request: {}, Detail: {}".format(url, data))
    return code, data
