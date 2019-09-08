import json
import re
import requests

import pandas as pd
import numpy as np

from seeq.sdk import *

from ...base import gconfig
from .. import _login


class Workbook:
    pass


class Analysis(Workbook):
    pass


def search(path=None, content_filter='owner', recursive=False):
    return _search(path, content_filter, recursive)


def _search(path_filter, content_filter, recursive, parent_id=None, parent_path=None):
    results_df = pd.DataFrame()

    path_filter_parts = None
    if path_filter is not None:
        path_filter_parts = re.split(r'\s*>>\s*', path_filter.strip())

    if parent_id is not None:
        folder_output_list = _get_folders(content_filter=content_filter,
                                          folder_id=parent_id)
    else:
        folder_output_list = _get_folders(content_filter=content_filter)

    for content in folder_output_list['content']:
        if path_filter_parts and content['name'] != path_filter_parts[0]:
            continue

        if not path_filter_parts:
            results_df = results_df.append({
                'ID': content['id'],
                'Type': content['type'],
                'Path': parent_path if parent_path else np.nan,
                'Name': content['name'],
                'Owner Name': content['owner']['name'],
                'Owner Username': content['owner']['username'] if 'username' in content['owner'] else np.nan,
                'Owner ID': content['owner']['id'],
                'Pinned': content['markedAsFavorite'],
                'Created At': content['createdAt'],
                'Updated At': content['updatedAt'],
                'Access Level': content['accessLevel']
            }, ignore_index=True)

        if content['type'] == 'Folder' and recursive:
            child_path_filter = None
            if path_filter_parts and len(path_filter_parts) > 1:
                child_path_filter = ' >> '.join(path_filter_parts[1:])

            if parent_path is None:
                new_parent_path = content['name']
            else:
                new_parent_path = parent_path + ' >> ' + content.name

            child_results_df = _search(child_path_filter, content_filter, recursive, content['id'], new_parent_path)

            results_df = results_df.append(child_results_df,
                                           ignore_index=True)

    return results_df


def _get_folders(content_filter='ALL', folder_id=None, archived=False, sort_order='createdAt ASC', only_pinned=False):
    # We have to make a "raw" REST request here because the get_folders API doesn't work well due to the
    # way it uses inheritance.
    api_client_url = gconfig.get_api_url()
    query_params = 'filter=%s&isArchived=%s&sortOrder=%s&limit=100000&onlyPinned=%s' % (
        content_filter,
        str(archived).lower(),
        sort_order,
        str(only_pinned).lower())

    request_url = api_client_url + '/folders?' + query_params

    if folder_id:
        request_url += '&folderId=' + folder_id

    response = requests.get(request_url, headers={
        "Accept": "application/vnd.seeq.v1+json",
        "x-sq-auth": _login.client.auth_token
    }, verify=Configuration().verify_ssl)

    return json.loads(response.content)
