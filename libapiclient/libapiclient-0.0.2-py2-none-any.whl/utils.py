from . import logger
from .const import ResponseType
from .const import SLOW_REQUEST_TIME
from .session_pool import SessionPool
from .exception import MaskSensitiveDataException
from .exception import RequestException
from .exception import ResponseParsingException

import json
import copy
import time
import traceback
from lxml import objectify


def mask_data(data, sensitive_fields):
    """
    Mask sensitive data
    :type data: dict|str
    :type sensitive_fields: list
    :rtype masked_data: dict
    :raise: ValueError if fail to convert data from str to dict
    """
    if isinstance(data, str):
        masked_data = json.loads(data)
    else:
        masked_data = copy.deepcopy(data)

    if sensitive_fields:
        for field in sensitive_fields:
            if field in masked_data:
                masked_data[field] = '****'

    return masked_data


def send_third_party_request(
    endpoint,
    data,
    method='POST',
    timeout=20,
    channel_name='3rd party',
    is_request_json=False,
    headers=None,
    sensitive_data=None,
    wraps_response=False,
    log_response_data=True,
    auth=None,
    response_type=ResponseType.JSON,
    files=None,
    request_session=SessionPool(),
):
    try:
        masked_data = mask_data(data, sensitive_data)
    except ValueError:
        # Programming error
        logger.error('[{}]send_third_party_request|cannot_mask_sensitive_data|data={}'.format(channel_name, data))
        logger.error(traceback.format_exc())
        raise MaskSensitiveDataException()

    logger.debug('[{}]third_party_request_start|endpoint={},params={},method={},headers={}'.format(channel_name, endpoint, masked_data, method, headers))
    request_start_time = time.time()
    try:
        if method == 'POST':
            if is_request_json:
                response = request_session.post(
                    endpoint,
                    json=data,
                    timeout=timeout,
                    headers=headers,
                    auth=auth,
                )
            elif files:
                response = request_session.post(
                    endpoint,
                    files=files,
                    timeout=timeout,
                    headers=headers,
                    auth=auth,
                )
            else:
                response = request_session.post(
                    endpoint,
                    data=data,
                    timeout=timeout,
                    headers=headers,
                    auth=auth,
                )
        elif method == 'PUT':
            if is_request_json:
                response = request_session.put(
                    endpoint,
                    json=data,
                    timeout=timeout,
                    headers=headers,
                    auth=auth,
                )
            else:
                response = request_session.put(
                    endpoint,
                    data=data,
                    timeout=timeout,
                    headers=headers,
                    auth=auth,
                )
        else:
            response = request_session.get(
                endpoint,
                params=data,
                timeout=timeout,
                headers=headers,
                auth=auth,
            )
    except:
        logger.error('[{}]request_exception|api={},params={},headers={}'.format(channel_name, endpoint, masked_data, headers))
        logger.error(traceback.format_exc())
        raise RequestException()

    response_to_log = response.content if log_response_data else '******'

    request_end_time = time.time()
    elapsed_time = int((request_end_time - request_start_time) * 1000)

    logger.info('[{}]third_party_request_end|endpoint={},params={},method={},req_headers={},resp_status={},resp_headers={},resp_content={},elapsed_time={}'.format(
        channel_name, endpoint, masked_data, method, headers, response.status_code, response.headers, response_to_log, elapsed_time))

    if elapsed_time > SLOW_REQUEST_TIME:
        logger.warn('[{}]third_party_request_slow_request|endpoint={},params={},method={},req_headers={},resp_status={},resp_headers={},resp_content={},elapsed_time={}'.format(
            channel_name, endpoint, masked_data, method, headers, response.status_code, response.headers, response_to_log, elapsed_time))

    try:
        if response_type == ResponseType.JSON:
            response = response.json()
        elif response_type == ResponseType.TEXT:
            response = response.content
        elif response_type == ResponseType.XML:
            response = objectify.fromstring(response.content).__dict__
        else:
            # NO_PARSING or unknow value, we return the requests Response object directly
            # and note that Response class supports membership testing, so our `if 'error' in result` test would work fine.
            pass
    except:
        logger.error('[%s]request_decode_exception|api=%s,params=%s,headers=%s,content=%s,response_type=%s',
            channel_name, endpoint, masked_data, headers, response.content, response_type)
        logger.error(traceback.format_exc())
        raise ResponseParsingException()

    if log_response_data:
        logger.info('[{}]third_party_request_formatted|api={},reply={}'.format(channel_name, endpoint, response))

    if wraps_response:
        # Warps response to avoid keywords conflict with internal convention
        return {'response': response}
    return response
