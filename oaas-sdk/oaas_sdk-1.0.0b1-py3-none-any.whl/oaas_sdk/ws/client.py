"""
Low-level interface with Webservice. Should not be used directly, instead, use the abstraction available in the `oaas_sdk.sdk` module.
"""
from typing import Iterable, Optional, Union

import pandas as pd
import pyarrow as pa
import requests

from oaas_sdk.objects import UnknownLabelingTask, ResultNotReady
from oaas_sdk.util import configuration


def get_labeling_task_status(labeling_task_id: str) -> str:
    """
    Gets the status of a labeling task
    Args:
        labeling_task_id
    Returns:
        One of [submitted, processed, failed, skipped, purged]
    """

    # Query
    r = requests.get("{}/labelingtask/{}".format(configuration.webservice_root, labeling_task_id), auth = (configuration.user, configuration.password))

    # Handle error cases
    if r.status_code == 404:
        raise UnknownLabelingTask("Unknown labeling task with id: {}".format(labeling_task_id))
    r.raise_for_status()

    # Success! return correct information
    ret = r.json()
    return ret['status']


def get_labeling_task_content(labeling_task_id: str) -> Union[str, pd.DataFrame]:
    """
    Gets the content of a labeling task
    Args:
        labeling_task_id
    Returns:
        String of json/csv, or DataFrame
    """
    # Query
    r = requests.get("{}/labelingtask/{}/content".format(configuration.webservice_root, labeling_task_id), auth = (configuration.user, configuration.password))

    # Handle error cases
    if r.status_code == 404:
        raise UnknownLabelingTask("Unknown labeling task with id: {}".format(labeling_task_id))
    if r.status_code == 425:
        raise ResultNotReady
    r.raise_for_status()

    # Success! return data
    if 'Content-Type' not in r.headers:
        raise RuntimeError("Content-Type not returned with webservice call. Unable to determine response type.")

    content_type = r.headers['Content-Type']
    if content_type in ('text/csv', 'application/json'):
        return r.text
    elif content_type == 'application/arrow':
        bites = r.content
        # noinspection PyTypeChecker
        df: pd.DataFrame = pa.deserialize(bites)
        return df
    else:
        raise RuntimeError("Unknown Content-Type returned: {}".format(content_type))


def create_new_labeling_task(labeling_solution_category: str, labeling_solution_name: str, data: pd.DataFrame, *,
                             companies: Optional[Iterable[str]] = None, output_format: str = 'arrow'):
    """
    Submits a new labeling task to be processed in the webservice. See the corresponding function in the SDK layer for expected values.
    Args:
        labeling_solution_category:
        labeling_solution_name:
        data:
        companies:
        output_format:
    Returns:
        Newly created labeling task's ID.
    """

    # Build params dictionary
    parameters = {}
    if companies:
        parameters['companies'] = list(companies)

    # Build arrow object
    _tuple = (data, parameters)
    bites = bytes(pa.serialize(_tuple).to_buffer())

    # Query
    headers = {'Content-Type': 'application/arrow'}
    params = {'output_format': output_format}
    r = requests.post("{}/labelingtask/new/{}/{}".format(configuration.webservice_root, labeling_solution_category, labeling_solution_name),
                      auth = (configuration.user, configuration.password), data = bites, headers = headers, params = params)

    # Check and return
    r.raise_for_status()

    # Success! return id
    ret = r.json()
    return ret['labeling_task_id']
