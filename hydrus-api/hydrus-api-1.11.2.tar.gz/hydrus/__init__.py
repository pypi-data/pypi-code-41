import enum
import io
import json
import warnings

import requests

DEFAULT_API_URL = 'http://127.0.0.1:45869/'


class HydrusAPIException(Exception):
    pass


class ConnectionError(HydrusAPIException):
    pass


class APIError(HydrusAPIException):
    def __init__(self, response):
        super().__init__(response.text)
        self.response = response


class MissingParameter(APIError):
    pass


class InsufficientAccess(APIError):
    pass


class ServerError(APIError):
    pass


@enum.unique
class Permission(enum.IntEnum):
    ImportURLs = 0
    ImportFiles = 1
    AddTags = 2
    SearchFiles = 3
    ManagePages = 4
    ManageCookies = 5


@enum.unique
class URLType(enum.IntEnum):
    PostURL = 0
    FileURL = 2
    GalleryURL = 3
    WatchableURL = 4
    # no matching URL Class
    UnknownURL = 5


@enum.unique
class ImportStatus(enum.IntEnum):
    # File not in database, ready for import (See documentation for "GET /add_urls/get_url_files")
    Importable = 0
    Success = 1
    Exists = 2
    PreviouslyDeleted = 3
    Failed = 4
    Vetoed = 7


@enum.unique
class TagAction(enum.IntEnum):
    Add = 0
    Delete = 1
    Pend = 2
    RescindPending = 3
    Petition = 4
    RescindPetition = 5


@enum.unique
class TagStatus(enum.IntEnum):
    Current = 0
    Pending = 1
    Deleted = 2
    Petitioned = 3


@enum.unique
class PageType(enum.IntEnum):
    GalleryDownloader = 1
    SimpleDownloader = 2
    HardDriveImport = 3
    Petitions = 5
    FileSearch = 6
    URLDownloader = 7
    Duplicates = 8
    ThreadWatcher = 9
    PageOfPages = 10


class RawClient:
    VERSION = 11

    _API_VERSION_ENDPOINT = '/api_version'
    _REQUEST_NEW_PERMISSIONS_ENDPOINT = '/request_new_permissions'
    _SESSION_KEY_ENDPOINT = '/session_key'
    _VERIFY_ACCESS_KEY_ENDPOINT = '/verify_access_key'

    _ADD_FILE_ENDPOINT = '/add_files/add_file'

    _CLEAN_TAGS_ENDPOINT = '/add_tags/clean_tags'
    _GET_TAG_SERVICES_ENDPOINT = '/add_tags/get_tag_services'
    _ADD_TAGS_ENDPOINT = '/add_tags/add_tags'

    _GET_URL_FILES_ENDPOINT = '/add_urls/get_url_files'
    _GET_URL_INFO_ENDPOINT = '/add_urls/get_url_info'
    _ADD_URL_ENDPOINT = '/add_urls/add_url'
    _ASSOCIATE_URL_ENDPOINT = '/add_urls/associate_url'

    _GET_COOKIES_ENDPOINT = '/manage_cookies/get_cookies'
    _SET_COOKIES_ENDPOINT = '/manage_cookies/set_cookies'

    _GET_PAGES_ENDPOINT = '/manage_pages/get_pages'
    _GET_PAGE_INFO_ENDPOINT = '/manage_pages/get_page_info'
    _FOCUS_PAGE_ENDPOINT = '/manage_pages/focus_page'

    _SEARCH_FILES_ENDPOINT = '/get_files/search_files'
    _FILE_METADATA_ENDPOINT = '/get_files/file_metadata'
    _FILE_ENDPOINT = '/get_files/file'
    _THUMBNAIL_ENDPOINT = '/get_files/thumbnail'

    def __init__(self, access_key=None, url=DEFAULT_API_URL):
        """See https://hydrusnetwork.github.io/hydrus/help/client_api.html for more information."""

        self._session = requests.session()
        self._access_key = access_key
        self._url = url.rstrip('/')

        api_version = self.api_version
        if self.VERSION != api_version:
            message = ('Version of API module (v{}) and API endpoint (v{}) differ, this might lead to '
                       'incompatibilities.'.format(self.VERSION, api_version))
            warnings.warn(message)

    def _call_endpoint(self, method, endpoint, **kwargs):
        if self._access_key:
            kwargs.setdefault('headers', {}).update({'Hydrus-Client-API-Access-Key': self._access_key})

        try:
            response = self._session.request(method, self._url + endpoint, **kwargs)
        except requests.ConnectionError as error:
            # Re-raise connection errors as hydrus.ConnectionErrors so these are more easy to handle for client
            # applications
            raise ConnectionError(*error.args)

        try:
            response.raise_for_status()
        except requests.HTTPError:
            if response.status_code == 400:
                raise MissingParameter(response)
            elif response.status_code in {401, 403, 419}:
                raise InsufficientAccess(response)
            elif response.status_code == 500:
                raise ServerError(response)
            raise APIError(response)

        return response

    @property
    def api_version(self):
        """Gets the current API version. I don't expect this to change much, but it might be important later."""

        response = self._call_endpoint('GET', self._API_VERSION_ENDPOINT)
        return response.json()['version']

    def request_new_permissions(self, name, permissions):
        """Register a new external program with the client. This requires the 'add from api request' mini-dialog under
        services->review services to be open, otherwise it will 403.

        Arguments:
            name: descriptive name of your access
            permissions: A list of numerical permission identifiers you want to request"""

        response = self._call_endpoint('GET', self._REQUEST_NEW_PERMISSIONS_ENDPOINT,
                                       params={'name': name, 'basic_permissions': json.dumps(permissions)})
        return response.json()['access_key']

    def session_key(self):
        """
        Get a new session key.
        """

        response = self._call_endpoint('GET', self._SESSION_KEY_ENDPOINT)
        return response.json()['session_key']

    def verify_access_key(self):
        """Check your access key is valid."""

        response = self._call_endpoint('GET', self._VERIFY_ACCESS_KEY_ENDPOINT)
        data = response.json()
        data['basic_permissions'] = [Permission(value) for value in data['basic_permissions']]
        return data

    def add_file(self, path_or_file):
        """Tell the client to import a file.

        Arguments:
            path_or_file: A path to a file or a readable file object"""

        if isinstance(path_or_file, str):
            response = self._call_endpoint('POST', self._ADD_FILE_ENDPOINT, json={'path': path_or_file})
        elif isinstance(path_or_file, io.BytesIO):
            response = self._call_endpoint('POST', self._ADD_FILE_ENDPOINT, data=path_or_file.read(),
                                           headers={'Content-Type': 'application/octet-stream'})
        else:
            raise ValueError('Value must be file object or path')

        data = response.json()
        data['status'] = ImportStatus(data['status'])
        return data

    def clean_tags(self, tags):
        """Ask the client about how it will see certain tags.

        Arguments:
            tags: a list of the tags you want cleaned"""

        response = self._call_endpoint('GET', self._CLEAN_TAGS_ENDPOINT, params={'tags': json.dumps(tags)})
        return response.json()['tags']

    def get_tag_services(self):
        """Ask the client about its tag services."""

        response = self._call_endpoint('GET', self._GET_TAG_SERVICES_ENDPOINT)
        return response.json()

    def add_tags(self, hashes, services_to_tags=None, services_to_actions=None, add_siblings_and_parents=True):
        """Make changes to the tags that files have.
        Arguments:
            hashes: a list of SHA256 hashes
            services_to_tags: a dict of service names to lists of tags to be 'added' to the files
            services_to_actions: a dict of service names to content update actions to lists of tags
            add_siblings_and_parents: an optional boolean, defaulting to true"""

        json_ = {'hashes': hashes, 'add_siblings_and_parents': add_siblings_and_parents}
        if services_to_tags:
            json_['service_names_to_tags'] = services_to_tags
        if services_to_actions:
            json_['service_names_to_actions_to_tags'] = services_to_actions

        self._call_endpoint('POST', self._ADD_TAGS_ENDPOINT, json=json_)

    def get_url_files(self, url):
        """Ask the client about an URL's files.

        Arguments:
            url: the url you want to ask about"""

        response = self._call_endpoint('GET', self._GET_URL_FILES_ENDPOINT, params={'url': url})
        data = response.json()
        for file_status in data['url_file_statuses']:
            file_status['status'] = ImportStatus(file_status['status'])

        return data

    def get_url_info(self, url):
        """Ask the client for information about a URL.

        Arguments:
            url: (the url you want to ask about)"""

        response = self._call_endpoint('GET', self._GET_URL_INFO_ENDPOINT, params={'url': url})
        data = response.json()
        data['url_type'] = URLType(data['url_type'])
        return data

    def add_url(self, url, page_name=None, show_page=False, service_to_tags=None):
        """Tell the client to 'import' a URL. This triggers the exact same routine as drag-and-dropping a text URL onto
        the main client window.

        Arguments:
            url: the url you want to ad
            page_name: optional page name to receive the url
            show_page : optional, defaulting to false, controls whether the UI will change pages on add
            service_to_tags: optional tags to give to any files imported from this url"""

        json_ = {'url': url, 'show_destination_page': show_page}
        if page_name:
            json_['destination_page_name'] = page_name
        if service_to_tags:
            json_['service_names_to_tags'] = service_to_tags

        response = self._call_endpoint('POST', self._ADD_URL_ENDPOINT, json=json_)
        return response.json()

    # Ignore parameters "url_to_add", "url_to_delete" and "hash" to make API simpler
    def associate_url(self, hashes, add=None, delete=None):
        """
        Manage which URLs the client considers to be associated with which files.

        Arguments:
            hashes: an SHA256 hash for a file in 64 characters of hexadecimal
            add: a list of urls you want to associate with the file(s)
            delete: a list of urls you want to disassociate from the file(s)"""

        json_ = {'hashes': hashes}
        if add:
            json_['urls_to_add'] = add
        if delete:
            json_['urls_to_delete'] = delete

        self._call_endpoint('POST', self._ASSOCIATE_URL_ENDPOINT, json=json_)

    def get_cookies(self, domain):
        """Get the cookies for a particular domain.

        Arguments:
            domain"""

        params = {'domain': domain}
        data = self._call_endpoint('GET', self._GET_COOKIES_ENDPOINT, params=params).json()
        return data['cookies']

    def set_cookies(self, cookies):
        """Set some new cookies for the client. This makes it easier to 'copy' a
        login from a web browser or similar to hydrus if hydrus's login system
        can't handle the site yet.

        Arguments:
            cookies: a list of cookie rows in the same format as returned by get_cookies()
        """

        self._call_endpoint('POST', self._SET_COOKIES_ENDPOINT, json={'cookies': cookies})

    def get_pages(self):
        """
        Get the page structure of the current UI session.
        """

        tree = self._call_endpoint('GET', self._GET_PAGES_ENDPOINT).json()['pages']

        def process_data(page):
            page['page_type'] = PageType(page['page_type'])
            for sub_page in page.get('pages', []):
                process_data(sub_page)

        process_data(tree)
        return tree

    # TODO: Convert enums for simple=False once this is more stable
    def get_page_info(self, page_key, simple=False):
        """
        https://www.youtube.com/watch?v=l_98K4_6UQ0

        Arguments:
            page_key: hexadecimal page_key as stated in /manage_pages/get_pages
            simple: true or false
        """
        params = {'page_key': page_key, 'simple': json.dumps(simple)}
        response = self._call_endpoint('GET', self._GET_PAGE_INFO_ENDPOINT, params=params)
        data = response.json()

        # Sometimes the data is wrapped in a page_info key
        data = data.get('page_info', data)
        # Sometimes the data is empty
        if not data:
            return

        data['page_type'] = PageType(data['page_type'])
        return data

    def focus_page(self, page_key):
        """
        'Show' a page in the main GUI, making it the current page in view. If it is already the current page, no change
        is made.

        Arguments:
            page_key : the page key for the page you wish to show
        """

        self._call_endpoint('POST', self._FOCUS_PAGE_ENDPOINT, json={'page_key': page_key})

    def search_files(self, tags, inbox=False, archive=False):
        """Search for the client's files.

        Arguments:
            tags: a list of tags you wish to search for
            inbox: true or false (optional, defaulting to false)
            archive: true or false (optional, defaulting to false)"""

        params = {'tags': json.dumps(tags), 'system_inbox': json.dumps(inbox), 'system_archive': json.dumps(archive)}
        response = self._call_endpoint('GET', self._SEARCH_FILES_ENDPOINT, params=params)
        return response.json()['file_ids']

    def file_metadata(self, hashes=None, file_ids=None, only_identifiers=False):
        """Get metadata about files in the client.

        Arguments:
            hashes: a list of hexadecimal SHA256 hashes
            file_ids: a list of numerical file ids
            only_identifiers: true or false (optional, defaulting to false)"""

        if not bool(hashes) ^ bool(file_ids):
            raise Exception('hashes (exclusive) or file_ids required')

        params = {}
        if hashes:
            params['hashes'] = json.dumps(hashes)
        if file_ids:
            params['file_ids'] = json.dumps(file_ids)
        if only_identifiers:
            params['only_return_identifiers'] = json.dumps(only_identifiers)

        response = self._call_endpoint('GET', self._FILE_METADATA_ENDPOINT, params=params)
        data = response.json()['metadata']
        if only_identifiers:
            return data

        for datum in data:
            services_to_statuses = datum['service_names_to_statuses_to_tags']
            for service, status_to_tags in services_to_statuses.items():
                for status, tags in list(status_to_tags.items()):
                    new_status = TagStatus(int(status))
                    services_to_statuses[service][new_status] = tags
                    del services_to_statuses[service][status]

        return data

    def get_file(self, hash_=None, file_id=None):
        """Get a file.

        Arguments:
            hash_: a hexadecimal SHA256 hash for the file
            file_id: numerical file id for the file"""

        if not bool(hash_) ^ bool(file_id):
            raise Exception('hash (exclusive) or file_id required')

        params = {}
        if hash_:
            params['hash'] = hash_
        elif file_id:
            params['file_id'] = file_id

        response = self._call_endpoint('GET', self._FILE_ENDPOINT, params=params)
        return response.content

    def get_thumbnail(self, hash_=None, file_id=None):
        """Get a file's thumbnail.

        Arguments:
            hash_: a hexadecimal SHA256 hash for the file
            file_id: numerical file id for the file"""

        if not bool(hash_) ^ bool(file_id):
            raise Exception('hash (exclusive) or file_id required')

        params = {}
        if hash_:
            params['hash'] = hash_
        elif file_id:
            params['file_id'] = file_id

        response = self._call_endpoint('GET', self._THUMBNAIL_ENDPOINT, params=params)
        return response.content


class Client(RawClient):

    def add_and_tag_files(self, paths_and_files, tags, services=('local tags',)):
        results = []
        hashes = set()
        for path_or_file in paths_and_files:
            result = self.add_file(path_or_file)
            results.append(result)
            hash_ = result.get('hash')
            if hash_:
                hashes.add(hash_)

        self.add_tags(list(hashes), {service: tags for service in set(services)})
        return results

    def get_pages(self, flatten=False):
        """
        Get the page structure of the current UI session.

        Arguments:
            flatten: Collapse the page tree into a list of pages
        """

        tree = super().get_pages()
        if not flatten:
            return tree

        pages = []

        def iterate_tree(page):
            pages.append(page)
            for sub_page in page.get('pages', []):
                iterate_tree(sub_page)

        iterate_tree(tree)
        return pages
