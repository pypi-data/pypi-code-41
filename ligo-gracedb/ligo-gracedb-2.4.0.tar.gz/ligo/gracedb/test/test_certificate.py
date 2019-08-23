import itertools
import pytest
try:
    from unittest import mock
except ImportError:  # py < 3
    import mock

from ligo.gracedb.rest import GraceDb


def test_x509_cert_load():
    """Test loading of X.509 certificate during client instantiation"""
    # Set up cert and key files
    cert_file = '/tmp/cert_file'
    key_file = '/tmp/key_file'

    conn_func = 'ligo.gracedb.rest.GraceDb.set_up_connector'
    load_cert_func = 'ligo.gracedb.rest.GraceDb._load_certificate'
    with mock.patch(conn_func), \
         mock.patch(load_cert_func) as mock_load_cert:  # noqa: E127

        # Initialize client
        g = GraceDb(cred=(cert_file, key_file))

    # Check credentials
    assert len(g.credentials) == 2
    assert g.auth_type == 'x509'
    assert g.credentials.get('cert_file') == cert_file
    assert g.credentials.get('key_file') == key_file
    assert mock_load_cert.called_once()


@pytest.mark.parametrize("reload_buffer", [86400, 10])
def test_x509_cert_expiration(reload_buffer, x509_cert):
    """Test X.509 certificate expiration check"""
    # Set up cert and key files
    cert_file = '/tmp/cert_file'
    key_file = '/tmp/key_file'

    conn_func = 'ligo.gracedb.rest.GraceDb.set_up_connector'
    load_cert_func = 'ligo.gracedb.rest.GraceDb._load_certificate'
    with mock.patch(conn_func), \
         mock.patch(load_cert_func):  # noqa: E127

        # Initialize client
        g = GraceDb(cred=(cert_file, key_file), reload_buffer=reload_buffer)

        # Assign fake certificate
        g.certificate = x509_cert

    # Check if certificate is expired (should have 3600 second lifetime)
    # compared to reload_buffer
    expired = g._check_certificate_expiration()
    if reload_buffer > 3600:
        assert expired is True
    else:
        assert expired is False


def test_x509_cert_autoload_in_expiration_check():
    """Test X.509 certificate loading during expiration check"""
    # Set up cert and key files
    cert_file = '/tmp/cert_file'
    key_file = '/tmp/key_file'

    conn_func = 'ligo.gracedb.rest.GraceDb.set_up_connector'
    load_cert_func = 'ligo.gracedb.rest.GraceDb._load_certificate'
    with mock.patch(conn_func), \
         mock.patch(load_cert_func) as mock_load_cert:  # noqa: E127

        # Initialize client
        g = GraceDb(cred=(cert_file, key_file))

        # Try to check certificate expiration
        err_str = "'GraceDb' object has no attribute 'certificate'"
        with pytest.raises(AttributeError, match=err_str):
            g._check_certificate_expiration()

    # Should have been two attempts to load the certificate:
    # one in the constructor and one in the expiration check
    assert mock_load_cert.call_count == 2


def test_load_certificate_with_auth_type_not_x509():
    """Make sure loading a certificate fails with non-X.509 auth type"""
    # Instantiate a client with no auth
    g = GraceDb(force_noauth=True)

    # Try to load the certificate
    err_str = "Can't load certificate for non-X.509 authentication."
    with pytest.raises(RuntimeError, match=err_str):
        g._load_certificate()


def test_check_certificate_with_auth_type_not_x509():
    """
    Make sure checking a certificate expiration fails with non-X.509 auth type
    """
    # Instantiate a client with no auth
    g = GraceDb(force_noauth=True)

    # Try to check the certificate expiration
    err_str = \
        "Can't check certificate expiration for non-X.509 authentication."
    with pytest.raises(RuntimeError, match=err_str):
        g._check_certificate_expiration()


# All possible combinations of True/False for the three variables
RELOAD_TEST_DATA = list(itertools.product((True, False), repeat=3))
@pytest.mark.parametrize("force_noauth,reload_cert,cert_expired",  # noqa: E302
                         RELOAD_TEST_DATA)
def test_reloading_feature(force_noauth, reload_cert, cert_expired):
    # Set up cert and key files
    cert_file = '/tmp/cert_file'
    key_file = '/tmp/key_file'

    set_up_conn_func = 'ligo.gracedb.rest.GraceDb.set_up_connector'
    get_conn_func = 'ligo.gracedb.rest.GraceDb.getConnection'
    adjust_response_func = 'ligo.gracedb.rest.GraceDb.adjustResponse'
    request_func = 'ligo.gracedb.rest.GraceDb.make_request'
    response_func = 'ligo.gracedb.rest.GraceDb.get_response'
    load_cert_func = 'ligo.gracedb.rest.GraceDb._load_certificate'
    cert_expire_func = \
        'ligo.gracedb.rest.GraceDb._check_certificate_expiration'
    with mock.patch(get_conn_func), \
         mock.patch(request_func), \
         mock.patch(adjust_response_func), \
         mock.patch(response_func), \
         mock.patch(set_up_conn_func) as mock_set_up_conn, \
         mock.patch(load_cert_func) as mock_load_cert, \
         mock.patch(cert_expire_func) as mock_cert_expire:  # noqa: E127

        # Set return value for mock_cert_expire
        mock_cert_expire.return_value = cert_expired

        # Initialize client
        g = GraceDb(
            cred=(cert_file, key_file),
            reload_certificate=reload_cert,
            force_noauth=force_noauth
        )

        # Try to make a request
        g.get("https://fakeurl.com")

        # Compile number of times which we expect certain functions to be
        # called
        check_cert_call_count = 0
        set_up_conn_call_count = 1
        load_cert_call_count = int(not force_noauth)

        if g.auth_type == 'x509' and reload_cert:
            check_cert_call_count += 1
            if cert_expired:
                load_cert_call_count += 1
                set_up_conn_call_count += 1

        # Compare to actual results
        assert mock_load_cert.call_count == load_cert_call_count
        assert mock_cert_expire.call_count == check_cert_call_count
        assert mock_set_up_conn.call_count == set_up_conn_call_count
