from simple_rest_client.api import API
from simple_rest_client.resource import Resource
from vgscli._version import __version__


class RouteResource(Resource):
    actions = {
        'retrieve': {'method': 'GET', 'url': 'rule-chains/{}'},
        'create': {'method': 'POST', 'url': 'rule-chains'},
        'list': {'method': 'GET', 'url': 'rule-chains'},
        'delete': {'method': 'DELETE', 'url': 'rule-chains/{}'},
        'update': {'method': 'PUT', 'url': 'rule-chains/{}'},
    }


env_url = {
    'dev': 'https://api.verygoodsecurity.io',
    'sandbox': 'https://api.sandbox.verygoodsecurity.com',
    'live': 'https://api.live.verygoodsecurity.com'
}


def create_api(tenant, environment, token):
    api = API(
        api_root_url=env_url[environment],
        params={},  # default params
        headers={
            'VGS-Tenant': tenant,
            'Content-Type': 'application/vnd.api+json',
            'Accept': 'application/vnd.api+json',
            'User-Agent': 'VGS CLI {}'.format(__version__),
            'Authorization': 'Bearer {}'.format(token)
        },  # default headers
        timeout=50,  # default timeout in seconds
        append_slash=False,  # append slash to final url
        json_encode_body=True,  # encode body as json
    )
    api.add_resource(resource_name='routes', resource_class=RouteResource)
    return api
