import json, re
from urllib import parse
from samslacker import api_requestor


def camelcase_to_dashcase(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class SamplifyResource(object):
    @classmethod
    def get_api_base(cls):
        return None

    @classmethod
    def get_object_url(cls):
        if cls == SamplifyResource:
            raise NotImplementedError('SamplifyResource is an abstract class.')
        return '/%s/' % str(parse.quote(camelcase_to_dashcase(cls.__name__), safe=''))


class CreateableResource(SamplifyResource):
    @classmethod
    def create(cls, data, token=None):
        requestor = api_requestor.ApiRequestor(token=token)
        return json.loads(requestor.post(cls.get_object_url(), data).content)


class Events(CreateableResource):
    pass
