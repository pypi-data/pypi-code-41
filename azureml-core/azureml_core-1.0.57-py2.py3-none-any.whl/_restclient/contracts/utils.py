# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# ---------------------------------------------------------

"""contracts utilities"""

import uuid
import datetime
import pytz
from azureml._restclient.constants import RUN_ID_EXPRESSION, METRIC_TYPE_EXPRESSION, AFTER_TIMESTAMP_EXPRESSION


DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


def get_new_id():
    """create an uuid string"""
    return str(uuid.uuid4())


def get_timestamp(return_as_string=True):
    """create a time stamp"""
    # Setting microsecond to 0, this removes the millisecond the resulting
    # string is formatted as YYYY-MM-DDTHH:MM:SS+HH:MM
    # https://stackoverflow.com/questions/2150739/
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    if return_as_string:
        now = now.strftime(DATE_TIME_FORMAT)
    return now


def string_timestamp(timestamp, return_as_string=True):
    return timestamp.strftime(DATE_TIME_FORMAT)


def get_run_ids_filter_expression(run_ids):
    """get run ids filter expression"""
    sep = " or "
    run_filter = [(RUN_ID_EXPRESSION + run_id) for run_id in run_ids]
    return sep.join(run_filter)


def get_metric_types_filter_expression(metric_types):
    sep = " or "
    metric_filter = [(METRIC_TYPE_EXPRESSION + metric_type) for metric_type in metric_types]
    return sep.join(metric_filter)


def get_after_timestamp_filter_expression(after_timestamp):
    return AFTER_TIMESTAMP_EXPRESSION + string_timestamp(after_timestamp)


def get_run_ids_and_metric_types_filter_expression(run_ids=None, metric_types=None, after_timestamp=None):
    if run_ids is None and metric_types is None and after_timestamp is None:
        return None
    filter_fields = []
    if run_ids is not None:
        filter_fields.append(get_run_ids_filter_expression(run_ids))
    if metric_types is not None:
        filter_fields.append(get_metric_types_filter_expression(metric_types))
    if after_timestamp is not None:
        filter_fields.append(get_after_timestamp_filter_expression(after_timestamp))

    sep = ") and ("
    return "({0})".format(sep.join(filter_fields))
