import inflect
import json
import re
from datetime import datetime, date

import api_requestor
import error

inflect_engine = inflect.engine()


def convert_to_piano_object(resp, klass_name=None):
    """
    Used to go deep into the object returned by the API converting dictionaries into Piano Objects.

    :param resp: The response object coming from API
    :type resp: object
    :param klass_name: The corresponding type of object to convert the dictionary
    :type klass_name: str
    :return: A new Piano object if able to convert or the original value
    :rtype: object
    """
    types = {
        'access': Access,
        'app': App,
        'conversion': Conversion,
        'export': Export,
        'inquiry': Inquiry,
        'list': ListObject,
        'offer': Offer,
        'promotion': Promotion,
        'resource': Resource,
        'subscription': Subscription,
        'term': Term,
        'user': User,
        'webhook': Webhook,
    }

    if isinstance(resp, list):
        return [convert_to_piano_object(i, klass_name) for i in resp]
    elif isinstance(resp, dict) and not isinstance(resp, PianoObject):
        resp = resp.copy()
        if isinstance(klass_name, basestring):
            klass = types.get(klass_name, PianoObject)
        else:
            klass = PianoObject
        return klass.construct_from(resp)
    else:
        return resp


class PublisherMixin(object):
    namespace = 'publisher'


class UserMixin(object):
    namespace = 'publisher/user'


class PianoObject(dict):
    id_map = 'id'
    namespace = None
    _original_values = None

    def __init__(self, id=None, klass_name=None, **params):
        super(PianoObject, self).__init__()

        self._retrieve_params = params
        self._klass_name = klass_name

        if id:
            self['id'] = id

    @classmethod
    def construct_from(cls, values, klass_name=None):
        """
        Creates an instance of the class from a dictionary

        :param values: Object returned by the API
        :type values: dict
        :param klass_name: Used from ListObject to convert the objects to the specified type.
        :type klass_name: str
        :return: instance
        :rtype: PianoObject
        """
        instance = cls(values.get(cls.id_map), klass_name=klass_name)
        instance.refresh_from(values, klass_name)
        return instance

    def refresh_from(self, values, klass_name=None):
        """
        Used to go through the object keys converting dictionaries into PianoObjects and unix
        timestamps into DateTimes

        :param values: Object returned by the API
        :type values: dict
        :param klass_name: Used from ListObject to convert the objects to the specified type.
        :type klass_name: str
        """
        for k, v in values.iteritems():
            if '_date' in k and isinstance(v, int):
                v = datetime.utcfromtimestamp(v)
            super(PianoObject, self).__setitem__(k, convert_to_piano_object(v, klass_name))

    def request(self, method, url, params=None, data=None, json=None, response_field_name=None,
                klass_name=None):
        """
        Wraps around requestor class

        :param method: HTTP Method
        :type method: str
        :param url: Url
        :type url: str
        :param params: (optional) Querystring params
        :type params: dict
        :param data: (optional) Body payload
        :type data: dict
        :param json: (optional) json data to send in the body of the :class:`Request`.
        :type json: dict
        :param response_field_name: (optional) Key from response object that contains the actual object
        :type response_field_name: str
        :param klass_name: (optional) PianoObject class to create an instance of
        :type klass_name: str
        :return: instance
        :rtype: PianoObject
        """
        if params is None:
            params = self._retrieve_params
        requestor = api_requestor.APIRequestor()
        response = requestor.request(method, url, params=params, data=data, json=json)

        instance = convert_to_piano_object(response[response_field_name], klass_name)
        instance._original_values = response[response_field_name]
        return instance


class ListObject(PianoObject):

    def list(self, **params):
        """
        Use to get a list of objects using the /list API endpoints from the current url and filters

        :param params: Request params/filters
        :type params: dict
        :return: ListObject
        :rtype: PianoObject
        """
        requestor = api_requestor.APIRequestor()
        response = requestor.request('get', self._url, params=params)

        try:
            # Set list in 'data' key for consistency
            response['data'] = response.pop(inflect_engine.plural(self._klass_name))
        except KeyError:
            pass

        piano_object = ListObject.construct_from(response, self._klass_name)
        piano_object._retrieve_params = params
        piano_object._url = self._url
        return piano_object

    def auto_paging_iter(self):
        """
        Used to iterate through the full list of objects without the need of manual pagination

        :return: List generator
        :rtype: list
        """
        page = self
        params = dict(self._retrieve_params)
        limit = page['limit']
        total = page['total']
        count = page['count']

        while True:
            item = None
            for item in page['data']:
                yield item

            offset = params.get('offset', 0)
            if item is None or offset + count == total:
                return

            params['offset'] = offset + limit
            page = self.list(**params)

    def __iter__(self):
        return getattr(self, 'data', []).__iter__()


class APIResource(PianoObject):

    @classmethod
    def retrieve(cls, id, **params):
        """
        Use to retrieve an specific object using the /get API endpoints

        :param id: The id of the object to retrieve
        :type id: str
        :param params: Request params
        :type params: dict
        :return: instance
        :rtype: PianoObject
        """
        instance = cls(id, **params)
        instance.refresh(response_field_name=cls.response_field_name(), klass_name=cls.class_name())
        return instance

    def instance_params(self, params=None):
        """
        Returns the request params adding the id corresponding to the specific object

        :param params: Request params
        :type params: dict
        :return: Request params
        :rtype: dict
        """
        if params is None:
            params = {}

        params = params.copy()
        id = self.get('id')
        if not id:
            raise error.InvalidRequestError(
                'Could not determine which URL to request: {} instance '
                'has invalid ID: {}'.format(type(self).__name__, id), 'id')

        params[self.id_map] = id
        return params

    def refresh(self, response_field_name, klass_name):
        """
        Use to retrieve an specific object using the /get API endpoints

        :param response_field_name: Key from response object that contains the actual object
        :type response_field_name: str
        :param klass_name: The corresponding type of object to convert the dictionary
        :type klass_name: str
        :return: instance
        :rtype: PianoObject
        """
        params = self.instance_params()
        url = '{}/{}'.format(self.class_url(), 'get')
        values = self.request(
            'get', url, params=params,
            response_field_name=response_field_name,
            klass_name=klass_name
        )
        self.refresh_from(values)
        self._original_values = values
        return self

    @classmethod
    def class_namespace(cls):
        """
        :return: Namespace use as prefix to build API endpoints urls
        :rtype: str
        """
        if cls == APIResource:
            raise NotImplementedError('APIResource is an abstract class.')
        return cls.namespace.lower()

    @classmethod
    def class_name(cls):
        """
        :return: Lowered class name
        :rtype: str
        """
        if cls == APIResource:
            raise NotImplementedError('APIResource is an abstract class.')
        return cls.__name__.lower()

    @classmethod
    def class_url(cls):
        """
        :return: Urls from namespace and class name
        :rtype: str
        """
        cls_namespace = cls.namespace
        url = '/'.join(re.findall('[A-Z][^A-Z]*', cls.__name__)).lower()
        return '{}/{}'.format(cls_namespace, url)

    @classmethod
    def response_field_name(cls):
        """
        :return: Key that contains the actual object in the API response
        :rtype: str
        """
        if cls == APIResource:
            raise NotImplementedError('APIResource is an abstract class.')
        return cls.class_name()


class ListableAPIResource(APIResource):

    @classmethod
    def list(cls, **params):
        """
        Use to get a list of objects using the /list API endpoints

        :param params: (optional) Request params/filters
        :type params: dict
        :return: ListObject
        :rtype: ListObject
        """
        klass_name = cls.class_name()
        requestor = api_requestor.APIRequestor()
        url = '{}/{}'.format(cls.class_url(), 'list')
        response = requestor.request('get', url, params=params)

        try:
            # Set list in 'data' key for consistency
            response['data'] = response.pop(inflect_engine.plural(klass_name))
        except KeyError:
            pass

        piano_object = ListObject.construct_from(response, klass_name)
        piano_object._retrieve_params = params
        piano_object._url = url
        return piano_object


# API objects
class Access(UserMixin, ListableAPIResource):
    id_map = 'access_id'

    @classmethod
    def _make_request(cls, http_method, endpoint, **params):
        requestor = api_requestor.APIRequestor()
        response = requestor.request(
            http_method, '{}/{}'.format(cls.class_url(), endpoint), params=params
        )
        return response

    @classmethod
    def check(cls, **params):
        klass_name = cls.class_name()
        response = cls._make_request('get', 'check', **params)
        return convert_to_piano_object(response[klass_name], klass_name)

    @classmethod
    def grant(cls, **params):
        klass_name = cls.class_name()
        response = cls._make_request('post', 'grant', **params)
        return convert_to_piano_object(response['data'][0], klass_name)

    @classmethod
    def update(cls, **params):
        klass_name = cls.class_name()
        response = cls._make_request('post', 'update', **params)
        return convert_to_piano_object(response[klass_name], klass_name)

    @classmethod
    def revoke(cls, access_id):
        klass_name = cls.class_name()
        response = cls._make_request('get', 'revoke', access_id=access_id)
        return convert_to_piano_object(response[klass_name], klass_name)


class App(PublisherMixin, ListableAPIResource):
    id_map = 'aid'


class Conversion(PublisherMixin, ListableAPIResource):
    id_map = 'term_conversion_id'


class Export(PublisherMixin, ListableAPIResource):
    id_map = 'export_id'


class Inquiry(PublisherMixin, ListableAPIResource):
    pass


class Offer(PublisherMixin, ListableAPIResource):
    id_map = 'offer_id'


class OfferTemplate(PublisherMixin, ListableAPIResource):
    id_map = 'offer_template_id'

    @classmethod
    def list(cls, **params):
        """
        Use to get a list of objects using the /list API endpoints
        Overrides base method to set default `order_by` parameter

        :param params: (optional) Request params/filters
        :type params: dict
        :return: ListObject
        :rtype: ListObject
        """
        if 'order_by' not in params:
            params['order_by'] = 'name'
        return super(OfferTemplate, cls).list(**params)

    @classmethod
    def response_field_name(cls):
        """
        Overrides base method as it doesn't follow the convention

        :return: Key that contains the actual object in the API response
        :rtype: str
        """
        return 'offer_template_version'


class Promotion(PublisherMixin, ListableAPIResource):
    id_map = 'promotion_id'


class Resource(PublisherMixin, ListableAPIResource):
    id_map = 'rid'


class Subscription(PublisherMixin, ListableAPIResource):
    id_map = 'subscription_id'

    @classmethod
    def retrieve(cls, **_):
        """
        API doesn't have a /get endpoint for subscriptions
        """
        raise NotImplementedError('Can\'t retrieve a single subscription. Use Subscription.list()')

    @classmethod
    def stats(cls, **params):
        klass_name = cls.class_name()
        requestor = api_requestor.APIRequestor()
        url = '{}/{}'.format(cls.class_url(), 'stats')
        response = requestor.request('post', url, params=params)

        try:
            # Set list in 'data' key for consistency
            response['data'] = response.pop(inflect_engine.plural(klass_name))
        except KeyError:
            pass

        piano_object = ListObject.construct_from(response, klass_name)
        piano_object._retrieve_params = params
        piano_object._url = url
        return piano_object

    @classmethod
    def update(cls, subscription_id, **params):
        params['subscription_id'] = subscription_id
        requestor = api_requestor.APIRequestor()
        url = '{}/{}'.format(cls.class_url(), 'update')
        response = requestor.request('post', url, params=params)
        return response['data']

    @classmethod
    def cancel(cls, subscription_id, refund_last_payment=False):
        params = {
            'subscription_id': subscription_id,
            'refund_last_payment': refund_last_payment,
        }
        requestor = api_requestor.APIRequestor()
        url = '{}/{}'.format(cls.class_url(), 'cancel')
        response = requestor.request('post', url, params=params)
        return response['data']


class Term(PublisherMixin, ListableAPIResource):
    id_map = 'term_id'


class User(PublisherMixin, ListableAPIResource):
    id_map = 'uid'
    _custom_fields = None

    def _set_custom_fields(self):
        if not self._custom_fields:
            custom_fields = {}
            for custom_field in self['custom_fields']:
                data_type = custom_field['dataType']
                value = custom_field['value']
                if data_type == 'BOOLEAN':
                    value = (custom_field['value'] is not None
                             and custom_field['value'].lower() == 'true')
                elif data_type == 'SINGLE_SELECT_LIST':
                    try:
                        value = json.loads(value)[0]
                    except (IndexError, TypeError):
                        value = ''
                custom_fields[custom_field['fieldName']] = value
            self._custom_fields = custom_fields
        return self._custom_fields

    @property
    def custom_fields(self):
        if not self._custom_fields:
            self._set_custom_fields()
        return self._custom_fields

    @classmethod
    def create(cls, **data):
        """
        Use to create an object using the /create API endpoints

        :param data: Payload to update the object from
        :type data: dict
        """
        instance = cls()
        url = '{}/{}'.format(cls.class_url(), 'register')
        return instance.request('post', url, data=data, response_field_name='data',
                                klass_name='user')

    def save(self):
        """
        Use to get a list of objects using the /update API endpoints

        """
        url = '{}/{}'.format(self.class_url(), 'update')
        data = self.custom_fields.copy()

        for key, value in data.items():
            try:
                custom_field = [x for x in self['custom_fields'] if x['fieldName'] == key][0]
            except IndexError:
                continue

            if custom_field['archived']:
                del data[key]
                continue

            data_type = custom_field['dataType']

            if data_type == 'SINGLE_SELECT_LIST':
                if value:
                    value = json.dumps([value])
                elif custom_field['favouriteOptions']:
                    value = json.dumps(custom_field['favouriteOptions'])
                else:
                    del data[key]
                    continue
            elif data_type == 'ISO_DATE':
                if isinstance(value, datetime):
                    value = value.date()
                if isinstance(value, date):
                    value = value.isoformat()
            data[key] = value

        params = {
            'uid': self['uid'],
            'first_name': self['first_name'],
            'last_name': self['last_name'],
        }
        self.request('post', url, params=params, json=data, response_field_name='user')

    def access_check(self, **params):
        params = self.instance_params(params)
        try:
            access = Access.check(**params)
        except KeyError:
            access = None
        return access

    def access_grant(self, **params):
        params = self.instance_params(params)
        try:
            access = Access.grant(**params)
        except KeyError:
            access = None
        return access

    def access_update(self, **params):
        params = self.instance_params(params)
        try:
            access = Access.update(**params)
        except KeyError:
            access = None
        return access

    def access_list(self, **params):
        params = self.instance_params(params)
        return Access.list(**params)

    def active_access_list(self, **params):
        access_list = self.access_list(**params)
        active_access_list = [x for x in access_list.auto_paging_iter() if x['granted']]
        return active_access_list

    def subscriptions(self, **params):
        params = self.instance_params(params)
        subscriptions = Subscription.stats(**params)
        return subscriptions

    def active_subscriptions(self, **params):
        subscriptions = self.subscriptions(**params)
        active_subscriptions = [x for x in subscriptions.auto_paging_iter() if x['status'] == 'A']
        return active_subscriptions

    def update_custom_field(self, name, value):
        try:
            self.custom_fields[name] = value
        except KeyError:
            raise KeyError('Custom field "{}" does not exist'.format(name))

    def update_custom_fields(self, fields):
        for key, value in fields.iteritems():
            try:
                self.update_custom_field(key, value)
            except KeyError:
                continue

    @classmethod
    def search(cls, **params):
        """
        Use to get a list of users using the /search API endpoints

        :param params: (optional) Request params/filters
        :type params: dict
        :return: ListObject
        :rtype: ListObject
        """
        klass_name = cls.class_name()
        requestor = api_requestor.APIRequestor()
        url = '{}/{}'.format(cls.class_url(), 'search')
        response = requestor.request('post', url, params=params)

        try:
            # Set list in 'data' key for consistency
            response['data'] = response.pop(inflect_engine.plural(klass_name))
        except KeyError:
            pass

        piano_object = ListObject.construct_from(response, klass_name)
        piano_object._retrieve_params = params
        piano_object._url = url
        return piano_object


class Webhook(PublisherMixin, ListableAPIResource):
    id_map = 'webhook_id'
