import datetime
import jwt
import requests
import logging

from collections.abc import Iterable
from http.cookiejar import CookiePolicy
from wrapt import ObjectProxy
from deprecated import deprecated
from http import HTTPStatus
from urllib.parse import urljoin, urlparse, parse_qs
from collections import defaultdict

from pypermedia import HypermediaClient
from requests_toolbelt.adapters import host_header_ssl

from dli import __version__
from dli.siren import siren_to_entity
from dli.client.auth import get_auth_key
from dli.client.components.auto_reg_metadata import AutoRegMetadata
from dli.client.components.collection import Collection
from dli.client.components.datafile import Datafile
from dli.client.components.dataset import Dataset, Dictionary
from dli.client.components.me import Me
from dli.client.components.package import Package
from dli.client.components.search import Search
from dli.client.exceptions import (
    DatalakeException, InsufficientPrivilegesException, InvalidPayloadException,
    UnAuthorisedAccessException, CatalogueEntityNotFoundException
)

from dli.siren import PatchedSirenBuilder

logger = logging.getLogger(__name__)


class DliClient(AutoRegMetadata, Collection, Datafile, Dataset,
                Me, Package, Search, Dictionary):
    """
    Definition of a client. This client mixes in utility functions for
    manipulating collections, packages, datasets and datafiles.
    """
    def __init__(self, api_key, api_root, host=None):
        self.api_key = api_key
        self.api_root = api_root
        self.host = host
        self._session = self._new_session()

    def _new_session(self):
        return Session(
            self.api_key,
            self.api_root,
            self.host,
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


class Response(ObjectProxy):

    def __init__(self, wrapped, builder, *args, **kwargs):
        super(Response, self).__init__(wrapped, *args, **kwargs)
        self.builder = builder

    @property
    def is_siren(self):
        return self.request.headers.get(
            'Content-Type', ''
        ).startswith('application/vnd.siren+json')

    def to_siren(self):
        # Pypermedias terminology, not mine
        python_object = self.builder._construct_entity(
            self.json()
        ).as_python_object()

        # Keep the response availible
        python_object._raw_response = self

        return python_object

    def to_many_siren(self, relation):
        return [
            siren_to_entity(c) for c in
            self.to_siren().get_entities(rel=relation)
        ]


class BlockAll(CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False


class Session(requests.Session):

    def __init__(self, api_key, api_root, host, auth_key=None):
        super().__init__()
        self.api_key = api_key
        self.api_root = api_root
        self.host = host
        self.auth_key = auth_key or get_auth_key(api_key, api_root, host)

        if host and urlparse(api_root).scheme == "https":
            self.mount(
                'https://',
                host_header_ssl.HostHeaderSSLAdapter()
            )

        # Preserve backwards compat
        self.request_session = self

        self.verify = True
        self.s3_keys = {}
        self.token_expires_on = self.get_expiration_date(self.auth_key)
        self.siren_builder = PatchedSirenBuilder(
            verify=self.verify,
            request_factory=self.request_factory
        )
        # Don't allow cookies to be set.
        # The new API will reject requests with both a cookie
        # and a auth header (as there's no predictiable crediential to choose).
        #
        # However the old API, once authenticate using a Bearer token will
        # as a side effect of a request return a oidc_id_token which matches
        # the auth header. This is ignored.
        self.cookies.set_policy(BlockAll())

    def request_factory(self, method=None, url=None, headers=None, files=None, data=None,
                        params=None, auth=None, cookies=None, hooks=None, json=None):
        # relative uri? make it absolute.
        if not urlparse(url).netloc:
            url = urljoin(str(self.api_root), str(url))     # python 2/3 nonsense

        if isinstance(data, Iterable):
            json = data
            data = None

        headers = headers or {}
        # populate headers
        if urlparse(url).path.startswith('/__api/'):
            # Only the old API uses this. We want to be able to
            # override this.
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
        hooks['response'] = self.make_hook()

        return requests.Request(
            method=method,
            url=url,
            headers=headers,
            files=files,
            data=data,
            params=params,
            auth=auth,
            hooks=hooks,
            json=json
        )

    def request(self, method, url, cert=None, verify=None,
                stream=None, proxies=None, timeout=None, allow_redirects=True, **kwargs):
        """Constructs a :class:`PreparedRequest <PreparedRequest>` for
        transmission and returns it. The :class:`PreparedRequest` has settings
        merged from the :class:`Request <Request>` instance and those of the
        :class:`Session`.
        :param request: :class:`Request` instance to prepare with this
            session's settings.
        :rtype: requests.PreparedRequest
        """
        # appreciate this is very ugly, attempting to maintain backwards compat
        req = self.request_factory(
            method=method.upper(),
            url=url,
            **kwargs
        )

        prep = self.prepare_request(req)

        proxies = proxies or {}

        settings = self.merge_environment_settings(
            prep.url, proxies, stream, verify, cert
        )

        # Send the request.
        send_kwargs = {
            'timeout': timeout,
            'allow_redirects': allow_redirects,
        }
        send_kwargs.update(settings)
        resp = self.send(prep, **send_kwargs)

        return resp

    @staticmethod
    @deprecated(reason='No longer used for anything - private method')
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
            request_factory=self.request_factory,
            session=self,
            builder=PatchedSirenBuilder,
            verify=self.verify
        )

    def make_hook(self):
        return self._response_hook

    def _response_hook(self, response, *args, **kwargs):
        # Appologies for the ugly code. The startswith siren check
        # is to make this onlly relevant to the old API.
        response = Response(response, self.siren_builder)

        if not response.ok:
            exceptions = defaultdict(
                lambda: DatalakeException,
                {HTTPStatus.BAD_REQUEST: InvalidPayloadException,
                 HTTPStatus.UNPROCESSABLE_ENTITY: InvalidPayloadException,
                 HTTPStatus.UNAUTHORIZED: UnAuthorisedAccessException,
                 HTTPStatus.FORBIDDEN: InsufficientPrivilegesException,
                 HTTPStatus.NOT_FOUND: CatalogueEntityNotFoundException}
            )

            try:
                message = response.json()
            except ValueError:
                message = response.text

            raise exceptions[response.status_code](
                message=message,
                params=parse_qs(urlparse(response.request.url).query),
                response=response,
            )

        return response
