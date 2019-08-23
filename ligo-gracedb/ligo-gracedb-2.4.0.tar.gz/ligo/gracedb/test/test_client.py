import pytest
try:
    from unittest import mock
except ImportError:  # py < 3
    import mock

from ligo.gracedb.rest import GraceDb


def test_provide_x509_cert_and_key():
    """Test client instantiation with provided certificate and key files"""
    # Set up cert and key files
    cert_file = '/tmp/cert_file'
    key_file = '/tmp/key_file'

    load_cert_func = 'ligo.gracedb.rest.GraceDb._load_certificate'
    with mock.patch('ligo.gracedb.rest.GraceDb.set_up_connector'), \
         mock.patch(load_cert_func):  # noqa: E127
        # Initialize client
        g = GraceDb(cred=(cert_file, key_file))

    # Check credentials
    assert len(g.credentials) == 2
    assert g.auth_type == 'x509'
    assert g.credentials.get('cert_file') == cert_file
    assert g.credentials.get('key_file') == key_file


def test_provide_x509_proxy():
    """Test client instantiation with provided combined proxy file"""
    # Set up combined proxy file
    proxy_file = '/tmp/proxy_file'

    load_cert_func = 'ligo.gracedb.rest.GraceDb._load_certificate'
    with mock.patch('ligo.gracedb.rest.GraceDb.set_up_connector'), \
         mock.patch(load_cert_func):  # noqa: E127
        # Initialize client
        g = GraceDb(cred=proxy_file)

    # Check credentials
    assert len(g.credentials) == 2
    assert g.auth_type == 'x509'
    assert g.credentials.get('cert_file') == proxy_file
    assert g.credentials.get('key_file') == proxy_file


USER_PASS_TEST_DATA = [
    {'username': 'user', 'password': 'pw'},
    {'username': 'user'},
    {'password': 'pwd'},
]
@pytest.mark.parametrize("user_and_or_pass", USER_PASS_TEST_DATA)  # noqa: E302
def test_provide_username_and_password(user_and_or_pass):
    """Test client instantiation with provided username and or password"""

    with mock.patch('ligo.gracedb.rest.GraceDb.set_up_connector'):
        # Initialize client - should fail if only one of username and
        # password is provided
        if not len(user_and_or_pass) == 2:
            err_str = 'Must provide both username AND password for basic auth'
            with pytest.raises(RuntimeError, match=err_str):
                g = GraceDb(**user_and_or_pass)
        else:
            g = GraceDb(**user_and_or_pass)

            assert len(g.credentials) == 2
            assert g.auth_type == 'basic'
            assert g.credentials.get('username') == \
                user_and_or_pass.get('username')
            assert g.credentials.get('password') == \
                user_and_or_pass.get('password')


def test_provide_all_creds():
    """Test providing all credentials to the constructor"""
    # Setup
    cert_file = '/tmp/cert_file'
    key_file = '/tmp/key_file'
    username = 'user'
    password = 'pw'

    # Initialize client
    load_cert_func = 'ligo.gracedb.rest.GraceDb._load_certificate'
    with mock.patch('ligo.gracedb.rest.GraceDb.set_up_connector'), \
         mock.patch(load_cert_func):  # noqa: E127
        g = GraceDb(
            cred=(cert_file, key_file), username=username, password=password
        )

    # Check credentials - should prioritze x509 credentials
    assert len(g.credentials) == 2
    assert g.auth_type == 'x509'
    assert g.credentials.get('cert_file') == cert_file
    assert g.credentials.get('key_file') == key_file


def test_x509_credentials_lookup():
    """Test lookup of X509 credentials"""
    # Setup
    cert_file = '/tmp/cert_file'
    key_file = '/tmp/key_file'

    # Initialize client
    load_cert_func = 'ligo.gracedb.rest.GraceDb._load_certificate'
    find_x509_func = 'ligo.gracedb.rest.GraceDb._find_x509_credentials'
    with mock.patch('ligo.gracedb.rest.GraceDb.set_up_connector'), \
         mock.patch(load_cert_func), \
         mock.patch(find_x509_func) as mock_find_x509:  # noqa: E127
        mock_find_x509.return_value = (cert_file, key_file)
        g = GraceDb()

    # Check credentials - should prioritze x509 credentials
    assert len(g.credentials) == 2
    assert g.auth_type == 'x509'
    assert g.credentials.get('cert_file') == cert_file
    assert g.credentials.get('key_file') == key_file


def test_x509_lookup_cert_key_from_envvars():
    """Test lookup of X509 cert and key from environment variables"""
    # Setup
    cert_file = '/tmp/cert_file'
    key_file = '/tmp/key_file'

    # Initialize client
    fake_creds_dict = {
        'X509_USER_CERT': cert_file,
        'X509_USER_KEY': key_file,
    }
    load_cert_func = 'ligo.gracedb.rest.GraceDb._load_certificate'
    os_environ_func = 'ligo.gracedb.rest.os.environ'
    with mock.patch('ligo.gracedb.rest.GraceDb.set_up_connector'), \
         mock.patch(load_cert_func), \
         mock.patch.dict(os_environ_func, fake_creds_dict):  # noqa: E127
        g = GraceDb()

    # Check credentials - should prioritze x509 credentials
    assert len(g.credentials) == 2
    assert g.auth_type == 'x509'
    assert g.credentials.get('cert_file') == cert_file
    assert g.credentials.get('key_file') == key_file


def test_x509_lookup_proxy_from_envvars():
    """Test lookup of X509 combined provxy file from environment variables"""
    # Setup
    proxy_file = '/tmp/proxy_file'

    # Initialize client
    os_environ_func = 'ligo.gracedb.rest.os.environ'
    load_cert_func = 'ligo.gracedb.rest.GraceDb._load_certificate'
    mock_environ_dict = {'X509_USER_PROXY': proxy_file}
    with mock.patch('ligo.gracedb.rest.GraceDb.set_up_connector'), \
         mock.patch(load_cert_func), \
         mock.patch.dict(os_environ_func, mock_environ_dict):  # noqa: E127
        g = GraceDb()

    # Check credentials - should prioritze x509 credentials
    assert len(g.credentials) == 2
    assert g.auth_type == 'x509'
    assert g.credentials.get('cert_file') == proxy_file
    assert g.credentials.get('key_file') == proxy_file


def test_basic_credentials_lookup():
    """Test client instantiation - look up basic auth creds from .netrc file"""
    # Set up credentials and mock_netrc return
    fake_creds = {
        'machine': 'fake.com',
        'login': 'fake_user',
        'password': 'fake_password',
    }
    conn_func = 'ligo.gracedb.rest.GraceDb.set_up_connector'
    find_x509_func = 'ligo.gracedb.rest.GraceDb._find_x509_credentials'
    safe_netrc = 'ligo.gracedb.rest.safe_netrc'
    with mock.patch(conn_func), \
         mock.patch(find_x509_func) as mock_find_x509, \
         mock.patch(safe_netrc) as mock_netrc:  # noqa: E127

        # Force lookup to not find any X509 credentials
        mock_find_x509.return_value = None
        # Mock return value from netrc lookup
        mock_netrc().authenticators.return_value = (
            fake_creds['login'], None, fake_creds['password'])

        # Initialize client
        g = GraceDb('https://{0}/api/'.format(fake_creds['machine']))

        # Check credentials
        assert len(g.credentials) == 2
        assert g.auth_type == 'basic'
        assert g.credentials.get('username') == fake_creds.get('login')
        assert g.credentials.get('password') == fake_creds.get('password')


@pytest.mark.parametrize("fail_if_noauth", [True, False])
def test_no_credentials(fail_if_noauth):
    """Test client instantiation with no credentials at all"""
    conn_func = 'ligo.gracedb.rest.GraceDb.set_up_connector'
    find_x509_func = 'ligo.gracedb.rest.GraceDb._find_x509_credentials'
    safe_netrc = 'ligo.gracedb.rest.safe_netrc'
    with mock.patch(conn_func), \
         mock.patch(find_x509_func) as mock_find_x509, \
         mock.patch(safe_netrc) as mock_netrc:  # noqa: E127

        # Force lookup to not find any X509 credentials
        mock_find_x509.return_value = None
        # Mock return value from netrc lookup
        mock_netrc().authenticators.return_value = None

        # Initialize client
        if fail_if_noauth:
            err_str = 'No authentication credentials found.'
            with pytest.raises(RuntimeError, match=err_str):
                g = GraceDb(fail_if_noauth=fail_if_noauth)
        else:
            g = GraceDb(fail_if_noauth=fail_if_noauth)

            # Check credentials
            assert len(g.credentials) == 0
            assert g.auth_type is None


def test_force_noauth():
    """Test forcing no authentication, even with X509 certs available"""
    # Setup
    cert_file = '/tmp/cert_file'
    key_file = '/tmp/key_file'

    # Initialize client
    conn_func = 'ligo.gracedb.rest.GraceDb.set_up_connector'
    environ_dict = 'ligo.gracedb.rest.os.environ'
    mock_environ_dict = {
        'X509_USER_CERT': cert_file,
        'X509_USER_KEY': key_file,
    }
    with mock.patch(conn_func), \
         mock.patch.dict(environ_dict, mock_environ_dict):  # noqa: E127

        # Initialize client
        g = GraceDb(force_noauth=True)

    # Check credentials
    assert len(g.credentials) == 0
    assert g.auth_type is None


@pytest.mark.parametrize("creds_found", [True, False])
def test_fail_if_noauth(creds_found):
    """Test failing if no authentication credentials are provided"""
    cert_file = '/tmp/cert_file'
    key_file = '/tmp/key_file'

    # Initialize client
    conn_func = 'ligo.gracedb.rest.GraceDb.set_up_connector'
    load_cert_func = 'ligo.gracedb.rest.GraceDb._load_certificate'
    find_x509_func = 'ligo.gracedb.rest.GraceDb._find_x509_credentials'
    safe_netrc = 'ligo.gracedb.rest.safe_netrc'
    with mock.patch(conn_func), \
         mock.patch(load_cert_func), \
         mock.patch(find_x509_func) as mock_find_x509, \
         mock.patch(safe_netrc) as mock_netrc:  # noqa: E127

        if not creds_found:
            # Force lookup to not find any X509 credentials
            mock_find_x509.return_value = None
            # Mock return value from netrc lookup
            mock_netrc().authenticators.return_value = None

            # Initialize client
            err_str = 'No authentication credentials found.'
            with pytest.raises(RuntimeError, match=err_str):
                g = GraceDb(fail_if_noauth=True)
        else:
            # Initialize client:
            g = GraceDb(cred=(cert_file, key_file), fail_if_noauth=True)

            # Check credentials
            assert len(g.credentials) == 2
            assert g.auth_type == 'x509'


def test_force_noauth_and_fail_if_noauth():
    with mock.patch('ligo.gracedb.rest.GraceDb.set_up_connector'):
        # Initialize client
        err_str = ('You have provided conflicting parameters to the client '
                   'constructor: fail_if_noauth=True and force_noauth=True.')
        with pytest.raises(ValueError, match=err_str):
            GraceDb(force_noauth=True, fail_if_noauth=True)
