# -*- coding: utf-8 -*-

from openbayestool.version import VERSION as __version__

import openbayestool.tracker

log_param = openbayestool.tracker.log_param
log_metric = openbayestool.tracker.log_metric
get_callback_url = openbayestool.tracker.get_callback_url
set_callback_url = openbayestool.tracker.set_callback_url
get_access_token = openbayestool.tracker.get_job_access_token
set_access_token = openbayestool.tracker.set_job_access_token

__all__ = [
    'log_param',
    'log_metric',
    'get_callback_url',
    'set_callback_url',
    'get_access_token',
    'set_access_token'
]