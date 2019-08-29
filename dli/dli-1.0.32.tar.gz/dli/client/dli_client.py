import datetime
import json as json_lib
import logging
from http import HTTPStatus
from json.decoder import JSONDecodeError
from urllib.parse import urljoin, urlparse

import jwt
import requests
from pypermedia import HypermediaClient
from pypermedia.client import SirenBuilder
from pypermedia.siren import SirenEntity, _create_action_fn
from requests_toolbelt.adapters import host_header_ssl

from dli import __version__
from dli.client.auth import get_auth_key
from dli.client.components.auto_reg_metadata import AutoRegMetadata
from dli.client.components.collection import Collection
from dli.client.components.datafile import Datafile
from dli.client.components.dataset import Dataset
from dli.client.components.me import Me
from dli.client.components.package import Package
from dli.client.components.search import Search
from dli.client.exceptions import (
    DatalakeException, InsufficientPrivilegesException, InvalidPayloadException,
    UnAuthorisedAccessException
)

logger = logging.getLogger(__name__)


class DliClient:
    """
    Definition of a client. This client mixes in utility functions for
    manipulating collections, packages, datasets and datafiles.
    """
    def __init__(self, api_key, api_root, host=None):
        self.api_key = api_key
        self.api_root = api_root
        self.host = host
        self._session = self._new_session()
        self._components = [
            component(client=self)
            for component in (
                AutoRegMetadata,
                Collection,
                Datafile,
                Dataset,
                Me,
                Package,
                Search,
            )
        ]
        self.methods = {
            method.__name__: method
            for method in (
                getattr(component, attr)
                for component in self._components
                for attr in dir(component)
                if not attr.startswith('_')
            )
            if callable(method)
        }

    def _new_session(self):
        return Session(
            self.api_key,
            self.api_root,
            self.host,
        )

    def __getattr__(self, item):
        if item in self.methods:
            return self.methods[item]
        else:
            raise AttributeError(
                f"'{type(self)}' object has no attribute '{item}'"
            )

    @property
    def session(self):
        # if the session expired, then reauth
        # and create a new context
        if self._session.has_expired:
            self._session = self._new_session()
        return self._session

    @property
    def ctx(self):
        """ Alias to self.session for backward compatibility.
        """
        return self.session

    def get_root_siren(self):
        return self.session.get_root_siren()


class Session:

    def __init__(self, api_key, api_root, host, auth_key=None):
        self.api_key = api_key
        self.api_root = api_root
        self.host = host
        self.auth_key = auth_key or get_auth_key(api_key, api_root, host)

        self.request_session = self.create_request_session(api_root, host)

        self.s3_keys = {}
        self.token_expires_on = self.get_expiration_date(self.auth_key)

    def request_factory(self, method=None, url=None, headers=None, files=None, data=None,
                        params=None, auth=None, cookies=None, hooks=None, json=None):
        # relative uri? make it absolute.
        if not urlparse(url).netloc:
            url = urljoin(str(self.api_root), str(url))     # python 2/3 nonsense

        # uri template substitution.
        pars = params if method == "GET" else data

        if pars:
            if '__json' in pars:
                js = json_lib.loads(pars['__json'])
                pars.update(js)
                del pars['__json']

        if pars and method == "GET":
            params = pars
        else:
            json = pars
            data = None

        # populate headers
        if not headers:
            headers = {}
        headers['Content-Type'] = "application/vnd.siren+json"
        headers["X-Data-Lake-SDK-Version"] = str(__version__)
        headers.update(self.get_header_with_auth())

        # if a host has been provided, then we need to set it on the header
        if self.host:
            headers['Host'] = self.host

        if not hooks:
            hooks = {}
        if 'response' not in hooks:
            hooks['response'] = []
        hooks['response'] = make_hook(self.api_root, self.get_header_with_auth)

        return requests.Request(
            method=method,
            url=url,
            headers=headers,
            files=files,
            data=data,
            params=params,
            auth=auth,
            cookies=cookies,
            hooks=hooks,
            json=json
        )


    @staticmethod
    def create_request_session(root, host):
        # build the requests sessions that pypermedia will use
        # to submit requests
        session = requests.Session()

        # when no dns is available and the user is using an ip address
        # to reach the catalogue
        # we need to force the cert validation to be against
        # the host header, and not the host in the uri
        # (we only do this if the scheme of the root is https)
        if host and urlparse(root).scheme == "https":
            session.mount(
                'https://',
                host_header_ssl.HostHeaderSSLAdapter()
            )

        return session

    @staticmethod
    def get_expiration_date(token):
        # use a default_timeout if the token can't be decoded
        # until the proper endpoint is added on the catalog
        default_timeout = (
            datetime.datetime.utcnow() +
            datetime.timedelta(minutes=55)
        )

        try:
            # get the expiration from the jwt auth token
            decoded_token = jwt.get_unverified_header(token)
            if 'exp' not in decoded_token:
                return default_timeout

            return datetime.datetime.fromtimestamp(
                decoded_token['exp']
            )

        except Exception:
            return default_timeout

    @property
    def has_expired(self):
        # by default we don't want to fail if we could not decode the token
        # so if the ``token_expiry`` is undefined we assume the session
        # is valid
        if not self.token_expires_on:
            return False
        return datetime.datetime.utcnow() > self.token_expires_on

    def get_header_with_auth(self):
        auth_header = "Bearer {}".format(self.auth_key)
        return {"Authorization": auth_header}

    def uri_with_root(self, relative_path):
        return "{}/{}".format(self.api_root, relative_path)

    def get_root_siren(self):
        return HypermediaClient.connect(
            self.api_root,
            session=self.request_session,
            request_factory=self.request_factory,
            builder=PatchedSirenBuilder,
            verify=True
        )


def make_hook(root, get_header):
    def _make_empty_response(r):
        import copy
        response = copy.deepcopy(r)
        response._content = b'{"class": ["none"]}'
        return response

    def _extract_error_response_message(r):
        try:
            return r.json()['errorText']
        except (JSONDecodeError, KeyError):
            return r.text

    def _response_hook(r, *args, **kwargs):
        if r.status_code in [
            HTTPStatus.CREATED,
            HTTPStatus.ACCEPTED,
            HTTPStatus.NO_CONTENT,
            HTTPStatus.NOT_FOUND
        ]:  # for now. or (300 <= r.status_code <= 399):
            return _make_empty_response(r)
        elif r.status_code in [
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.UNPROCESSABLE_ENTITY
        ]:
            raise InvalidPayloadException(_extract_error_response_message(r))
        elif r.status_code == HTTPStatus.UNAUTHORIZED:
            raise UnAuthorisedAccessException(_extract_error_response_message(r))
        elif r.status_code == HTTPStatus.FORBIDDEN:
            raise InsufficientPrivilegesException(_extract_error_response_message(r))
        elif r.status_code > HTTPStatus.BAD_REQUEST:
            raise DatalakeException(_extract_error_response_message(r))

    return _response_hook


class PatchedSirenBuilder(SirenBuilder):

    def _construct_entity(self, entity_dict):
        """
        We need to patch the actions as there is no ``radio`` support
        on the current pypermedia version.

        To avoid code duplication, this function will attempt to call the parent
        and replace the created actions with our custom ones.
        """

        # pypermedia does not like any custom attributes
        # not even those in the spec
        for action in entity_dict.get("actions", []):
            if "allowed" in action:
                del action["allowed"]

        entity = super(PatchedSirenBuilder, self)._construct_entity(entity_dict)

        return PatchedSirenEntity(
            classnames=entity.classnames,
            properties=entity.properties,
            actions=entity.actions,
            links=entity.links,
            entities=entity.entities,
            rel=entity.rel,
            verify=entity.verify,
            request_factory=entity.request_factory
        )


def _patched_make_request(self, _session=None, verify=None, **kwfields):
    """ The purpose of this is to override the `SirenAction.make_request` in
        pypermedia, which ignores the passed `verify` argument and just uses
        the one defined on self, while the one passed into the function gets
        swallowed into `kwfields` and sent in the request.
    """
    if verify is None:
        verify = self.verify
    s = _session or requests.Session()
    return s.send(self.as_request(**kwfields), verify=verify)


class PatchedSirenEntity(SirenEntity):

    def as_python_object(self):
        ModelClass = type(str(self.get_primary_classname()), (), self.properties)

        siren_builder = PatchedSirenBuilder(verify=self.verify, request_factory=self.request_factory)
        # add actions as methods
        for action in self.actions:
            # patch make_request to resolve InsecureRequestWaring problems (see DL-1961)
            action.make_request = _patched_make_request.__get__(action, type(action))
            method_name = SirenEntity._create_python_method_name(action.name)
            method_def = _create_action_fn(action, siren_builder)
            setattr(ModelClass, method_name, method_def)

        # add links as methods
        for link in self.links:
            for rel in link.rel:
                method_name = SirenEntity._create_python_method_name(rel)
                siren_builder = PatchedSirenBuilder(verify=self.verify, request_factory=self.request_factory)
                method_def = _create_action_fn(link, siren_builder)

                setattr(ModelClass, method_name, method_def)

        def get_entity(obj, rel):
            matching_entities = self.get_entities(rel) or []
            for x in matching_entities:
                yield x.as_python_object()

        setattr(ModelClass, 'get_entities', get_entity)

        return ModelClass()
