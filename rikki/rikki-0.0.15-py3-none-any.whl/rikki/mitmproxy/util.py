from mitmproxy import http
from rikki.mitmproxy.model import Request, Response
from typing import List, Optional, Dict
from mitmproxy.coretypes import multidict
from mitmproxy.net.http import Headers


def replace(flow: http.HTTPFlow, request: Optional[Request] = None, response: Optional[Response] = None):
    if request:
        if request.host:
            flow.request.host = request.host
        if request.content:
            flow.request.content = request.content.encode("utf8")
        if request.params:
            for item in request.params.items():
                flow.request.query.set_all(item[0], [item[1]])
        if request.headers:
            for item in request.headers.items():
                headers: Headers = flow.request.headers
                headers.set_all(item[0], [item[1]])
    if response:
        if response.headers:
            for item in response.headers.items():
                headers: Headers = flow.response.headers
                headers.set_all(item[0], [item[1]])
        if response.content:
            flow.response.content = response.content.encode("utf8")
        if response.code:
            flow.response.status_code = response.code


def filter(
        flows: List[http.HTTPFlow],
        request: Optional[Request] = None,
        response: Optional[Response] = None
) -> List[http.HTTPFlow]:
    """
    Filter flows and return only those that contain data from filter params
    :param flows: list of flows to be filtered
    :param request: request data to look for during filter
    :param response: response data to look for during filter
    :return: new list of filtered flows
    """
    result: List[http.HTTPFlow] = []
    result.extend(flows)

    for flow in result:
        if request:
            if request.host and request.host != flow.request.host:
                if flow in result:
                    result.remove(flow)
                continue
            if request.params and not contains_params(flow.request.query, request.params):
                if flow in result:
                    result.remove(flow)
                continue
            if request.content and not request.content.lower().strip() != flow.request.content.lower().strip():
                if flow in result:
                    result.remove(flow)
            if request.headers and not contains_headers(flow.request.headers, request.headers):
                if flow in result:
                    result.remove(flow)
        if response:
            if response.code and response.code != flow.response.status_code:
                if flow in result:
                    result.remove(flow)
            if response.headers and not contains_headers(flow.response.headers, response.headers):
                if flow in result:
                    result.remove(flow)
            if response.content and flow.response.content \
                    and response.content.lower().strip() != flow.response.content.decode("utf8").lower().strip():
                if flow in result:
                    result.remove(flow)

    return result


def contains_params(base: multidict.MultiDictView, candidate: Dict) -> bool:
    for key in candidate.keys():
        if key in base.keys() and candidate[key] in base.get_all(key):
            continue
        else:
            return False
    return True


def contains_headers(headers: Headers, candidate: Dict[str, str]):
    for key in candidate.keys():
        if key in headers.keys() and candidate[key] in headers.get_all(key):
            continue
        else:
            return False
    return True
