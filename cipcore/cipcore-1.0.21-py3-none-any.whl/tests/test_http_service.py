import responses
from requests import Session, Response, adapters
from mock import MagicMock

from cipcore import CipSession

cip_requests = CipSession(3)


@responses.activate
def test_cip_requests_response_integrity():
    responses.add(responses.GET, "http://test.com", json={}, status=200)
    response_object = cip_requests.get("http://test.com")
    assert(isinstance(cip_requests, Session))
    assert(isinstance(cip_requests.adapters['http://'], adapters.HTTPAdapter))
    assert(isinstance(cip_requests.adapters['https://'], adapters.HTTPAdapter))
    assert(isinstance(response_object, Response))


@responses.activate
def test_cip_requests_success():
    responses.add(responses.GET, "http://test.com", json={}, status=200)
    response_object = cip_requests.get("http://test.com")
    assert(response_object.ok)
    assert(response_object.status_code == 200)


@responses.activate
def test_cip_requests_receiving_client_error():
    responses.add(responses.GET, "http://test.com", json={}, status=400)
    response_object = cip_requests.get("http://test.com")
    assert(not response_object.ok)
    assert(response_object.status_code == 400)


@responses.activate
def test_cip_requests_receiving_server_error():
    responses.add(responses.GET, "http://test.com", json={}, status=500)
    response_object = cip_requests.get("http://test.com")
    assert(not response_object.ok)
    assert(response_object.status_code == 500)
