from time import sleep
import pytest
from multisafepay.transaction import Transaction, MSPError, get_status
from .testhttpserver import MSPTestServer


@pytest.fixture(scope="module")
def wsgiserver(request):
    srv = MSPTestServer()
    srv.run()
    # give some time to start server
    sleep(1)
    print("wsgi started")
    yield srv
    srv.stop()


def test_msp_ok(wsgiserver):
    transaction = Transaction(
        account="a",
        site_id="b",
        site_secure_code="c",
        notification_url="http://localhost/notify",
        cancel_url="",
        locale="nl_NL",
        ipaddress="1.2.3.4",
        email="test@example.com",
        transaction_id="1234",
        amount="2300",
        description="party",
        api_url="http://localhost:9000/ok",
        redirect_url="http://localhost:9000/success",
    )
    res = transaction.start()
    assert res == "http://localhost:9000/paylink"


def test_msp_error(wsgiserver):
    transaction = Transaction(
        account="a",
        site_id="b",
        site_secure_code="c",
        notification_url="http://localhost/notify",
        cancel_url="",
        locale="nl_NL",
        ipaddress="1.2.3.4",
        email="test@example.com",
        transaction_id="1234",
        amount="2300",
        description="party",
        api_url="http://localhost:9000/error",
        redirect_url="http://localhost:9000/success",
    )
    pytest.raises(MSPError, transaction.start)


def test_status(wsgiserver):
    status = get_status(
        account="a",
        site_id="b",
        site_secure_code="c",
        transaction_id="1234",
        api_url="http://localhost:9000/status_ok",
        redirect_url="http://localhost:9000/success",
    )
    assert status == "completed"


def test_status_error(wsgiserver):
    pytest.raises(
        MSPError,
        get_status,
        account="a",
        site_id="b",
        site_secure_code="c",
        transaction_id="1234",
        api_url="http://localhost:9000/status_error",
    )
