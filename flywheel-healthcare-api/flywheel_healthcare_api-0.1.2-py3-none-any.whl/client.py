"""Healthcare API client module."""
import time

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient import discovery
from googleapiclient.discovery import Resource
from requests.compat import basestring, urlencode, urlunparse
from requests.utils import requote_uri, to_key_val_list
from urllib3.util import parse_url

from .cache import FileCache

SHORTCUTS = {
    'locations': ['projects'],
    'datasets': ['projects', 'locations'],
    'operations': ['projects', 'locations', 'datasets'],
    'annotationStores': ['projects', 'locations', 'datasets'],
    'annotations': ['projects', 'locations', 'datasets', 'annotationStores'],
    'dicomStores': ['projects', 'locations', 'datasets'],
    'fhirStores': ['projects', 'locations', 'datasets'],
    'hl7V2Stores': ['projects', 'locations', 'datasets'],
}

SPECIAL_NAMES = {
    'observationLastn': 'Observation-lastn',
    'patientEverything': 'Patient-everything',
    'resourcePurge': 'Resource-purge'
}


class Client:
    """Healthcare API client class."""

    def __init__(self, token=None, credentials=None, version='v1beta1'):
        """Initialize a BaseClient instance."""
        super().__init__()
        self.project = None
        if token:
            self._credentials = Credentials(token=token)
        elif credentials:
            self._credentials = credentials
        else:
            self._credentials, self.project = google.auth.default()
        self._service = discovery.build('healthcare', version, credentials=self._credentials, cache=FileCache())

    def __dir__(self):
        return dir(self.__class__) + list(SHORTCUTS.keys())

    @classmethod
    def location_path(cls, project, location):
        """Return a fully-qualified location string."""
        return 'projects/{}/locations/{}'.format(project, location)

    @classmethod
    def dataset_path(cls, project, location, dataset):
        """Return a fully-qualified dataset string."""
        return 'projects/{}/locations/{}/datasets/{}'.format(
            project, location, dataset)

    @classmethod
    def store_path(cls, project, location, dataset, store_type, store):
        """Return a fully-qualified store string."""
        store_type = store_type.replace('v2', 'V2')  # hl7 special case
        return 'projects/{}/locations/{}/datasets/{}/{}Stores/{}'.format(
            project, location, dataset, store_type, store)

    @classmethod
    def fhir_resource_path(cls, project, location, dataset, store, resource_type, resource_id):
        """Return a fully-qualified FHIR resource string."""
        return 'projects/{}/locations/{}/datasets/{}/fhirStores/{}/fhir/{}/{}'.format(
            project, location, dataset, store, resource_type, resource_id)

    @classmethod
    def table_uri(cls, project, dataset, table):
        """Return a BigQuery table uri."""
        return 'bq://{}.{}.{}'.format(project, dataset, table)

    def __getattr__(self, name):
        attr = None
        for lvl in SHORTCUTS[name]:
            if not attr:
                attr = getattr(self._service, lvl)()
            else:
                attr = getattr(attr, lvl)()

        return ResourceWrapper(getattr(attr, name)(), name, self)

    def wait_operation(self, operation, sleep=10, timeout=None):
        """Wait for an operation to finish."""
        start = time.time()
        if not operation.get('done'):
            if timeout is not None and time.time() > start + timeout:
                message = 'Wait timeout: exceeded {}s for {}'.format(timeout, operation['name'])
                raise GCPError(response=operation, message=message)
            if operation.get('error'):
                message = 'Operation failed'
                raise GCPError(response=operation, message=message)
            operation = self.operations.get(name=operation['name'])
            time.sleep(sleep)
        return operation


class ResourceWrapper:
    """Wrapper class for the googleapiclient.discovery.Resource class.

    This class allows accessing the Resource class` attributes in an easier way.
    In case of paging results it will return a generator and handles page requests under the hood.
    """

    def __init__(self, resource, resource_name, client):
        self.resource = resource
        self.resource_name = resource_name
        self.request = None
        self._client = client

    def __getattr__(self, name):
        if name == 'list':
            def method(*args, **kwargs):
                self.request = getattr(self.resource, name)(*args, **kwargs)
                while True:
                    response = self.request.execute()
                    for r in response.get(self.resource_name, []):
                        yield r

                    if not response.get('nextPageToken'):
                        break
                    else:
                        self.request = self.resource.list_next(
                            previous_request=self.request,
                            previous_response=response
                        )
        elif name == 'dicomWeb':
            def method(*args, **kwargs):
                return dicom_web(self._client, *args, **kwargs)
        else:
            name = SPECIAL_NAMES.get(name, name)
            attr = getattr(self.resource, name)
            if attr.__name__ == 'methodResource':
                attr = attr()

            if isinstance(attr, Resource):
                return ResourceWrapper(attr, name, self._client)
            else:
                def method(*args, **kwargs):
                    params = kwargs.pop('params', {})
                    self.request = attr(*args, **kwargs)
                    scheme, auth, host, port, path, query, fragment = parse_url(self.request.uri)
                    # Carefully reconstruct the network location
                    netloc = auth or ''
                    if netloc:
                        netloc += '@'
                    netloc += host
                    if port:
                        netloc += ':' + str(port)

                    # Bare domains aren't valid URLs.
                    if not path:
                        path = '/'
                    enc_params = self._encode_params(params)
                    if enc_params:
                        if query:
                            query = '%s&%s' % (query, enc_params)
                        else:
                            query = enc_params

                    url = requote_uri(urlunparse([scheme, netloc, path, None, query, fragment]))
                    self.request.uri = url
                    return self.request.execute()
        try:
            # pylint: disable=protected-access
            setattr(method, '__doc__', self.resource._resourceDesc['methods'][name]['description'])
        except KeyError:
            pass
        return method

    def __dir__(self):
        additional_attrs = []
        if self.resource_name == 'dicomStores':
            additional_attrs.append('dicomWeb')
        if self.resource_name == 'fhir':
            additional_attrs += list(SPECIAL_NAMES.keys())
        return dir(self.__class__) + dir(self.resource) + additional_attrs

    @staticmethod
    def _encode_params(data):
        """Encode parameters in a piece of data.

        Will successfully encode parameters when passed as a dict or a list of
        2-tuples. Order is retained if data is a list of 2-tuples but arbitrary
        if parameters are supplied as a dict.
        """

        if isinstance(data, (str, bytes)):
            return data
        elif hasattr(data, 'read'):
            return data
        elif hasattr(data, '__iter__'):
            result = []
            for k, vs in to_key_val_list(data):
                if isinstance(vs, basestring) or not hasattr(vs, '__iter__'):
                    vs = [vs]
                for v in vs:
                    if v is not None:
                        result.append(
                            (k.encode('utf-8') if isinstance(k, str) else k,
                             v.encode('utf-8') if isinstance(v, str) else v))
            return urlencode(result, doseq=True)
        else:
            return data


def dicom_web(api_client, name):
    """Get a dicomweb-client instance for the given DICOM store.

    Arguments:
        store {string} -- The name of the DICOM store.

    Returns:
        [DICOMwebClient] -- DICOMwebClient instance.
    """
    # pylint: disable=protected-access
    url = '{}/{}/dicomWeb'.format(api_client._service._rootDesc['version'], name)
    # late import to enable using module without feature/dependency
    import dicomweb_client.api  # pylint: disable=import-error
    client = dicomweb_client.api.DICOMwebClient(api_client._service._baseUrl + url)
    # patch session used in dicomweb client to use tokens
    # pylint: disable=protected-access
    session = client._session
    request = session.request

    def auth_request(*args, **kwargs):
        r = Request()
        headers = kwargs['headers']
        api_client._credentials.before_request(r, *args, headers=headers)
        kwargs['headers'] = headers
        return request(*args, **kwargs)
    session.request = auth_request
    return client


class GCPError(Exception):
    """GCPError class."""

    def __init__(self, response=None, message=None, status_code=None):
        """Initialize a GCPError instance."""
        if response == message is None:
            raise TypeError('response or message required')
        self.status_code = status_code or (response.status_code if response else None)
        self.message = message or self.get_message(response)
        if self.status_code is not None:
            self.message = '{}: {}'.format(self.status_code, self.message)
        super().__init__(self.message)

    @staticmethod
    def get_message(response):
        """Get error message of a respone."""
        try:
            return response.json()['error']['message']
        except Exception:  # pylint: disable=broad-except
            return response.content
