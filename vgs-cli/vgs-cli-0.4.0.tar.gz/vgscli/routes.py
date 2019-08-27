import yaml

from collections import OrderedDict


class literal(str):
    pass


class quoted(str):
    pass


def quoted_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')


def literal_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')


def ordered_dict_presenter(dumper, data):
    return dumper.represent_dict(data.items())


yaml.add_representer(quoted, quoted_presenter)
yaml.add_representer(OrderedDict, ordered_dict_presenter)
yaml.add_representer(literal, literal_presenter)


def dump_yaml(data):
    return yaml.dump(data, default_flow_style=False, indent=2, width=1024)


def dump_all_routes(api):
    result = api.routes.list()
    body = result.body

    results = normalize(body['data'])

    updated = {
        'version': 1,
        'data': results,
    }

    return dump_yaml(updated)


def sync_all_routes(api, dump_data, route_process_listener=None):
    return __write_routes(dump_data, route_process_listener,
        lambda route_id, payload: api.routes.update(route_id, body=payload))


def normalize(results):
    # https://stackoverflow.com/a/8641732/6084
    # this `literal` function will ensure that we get a multi line string
    for result in results:
        if 'attributes' not in result:
            continue

        for filter in result['attributes']['entries']:
            if filter['operations']:
                filter['operations'] = literal(filter['operations'])
    return results


def __write_routes(dump_data, route_process_listener, api_call_function):
    payloads = yaml.load(dump_data)
    results = []
    for route in payloads['data']:
        route_id = route['id']
        payload = {'data': route}
        result = api_call_function(route_id, payload)
        if route_process_listener:
            route_process_listener(route_id)
        results.append(result.body['data'])

    results = normalize(results)

    updated = {
        'version': 1,
        'data': results,
    }

    return dump_yaml(updated)
