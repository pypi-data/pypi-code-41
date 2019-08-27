import requests

from metricfarmer.exceptions import ExtensionException


def source_rest(**kwargs):
    url = kwargs.get('url', None)
    user = kwargs.get('user', None)
    password = kwargs.get('password', None)
    headers = kwargs.get('headers', {'content-type': 'application/json'})
    method = kwargs.get('method', 'GET')
    payload = kwargs.get('payload', None)
    no_escape = kwargs.get('no_escape', False)
    result_call = kwargs.get('result_call', None)

    if not isinstance(headers, dict):
        raise ExtensionException('Given headers must be a dictionary')

    if url is None:
        raise ExtensionException('Url for source rest must be provided.')

    if method.upper() not in ['GET', 'POST', 'PUT']:
        raise ExtensionException('Method must be GET, POST or PUT. Other methods are not supported.')

    if bool(user) ^ bool(password):
        raise Exception('Both parameters user and password must be set, if already one is given.')

    parameters = {
        'method': method,
        'url': url,
        'headers': headers
    }

    if method.upper() in ['POST', 'PUT'] and payload is not None:
        parameters['json'] = payload
    elif method.upper() in ['GET'] and payload is not None:
        if not no_escape:
            parameters['params'] = payload
        else:
            param_elements = []
            for name, value in payload.items():
                param_elements.append('{}={}'.format(name, value))

            param_string = '?' + '&'.join(param_elements)

            parameters['url'] += param_string

    if user is not None and password is not None:
        parameters['auth'] = (user, password)

    rest_result = requests.request(**parameters)

    if rest_result.status_code >= 300:
        raise ExtensionException("Server send error code: {status}.\nReason: {error}".format(
            status=rest_result.status_code, error=rest_result.text))
    try:
        metric_result = eval(result_call, {'result': rest_result.json()})
    except Exception as e:
        raise ExtensionException("Errors occurred during evaluating result_call: {call}.\nError: {error} ".format(
            call=result_call, error=e
        ))
    return metric_result


