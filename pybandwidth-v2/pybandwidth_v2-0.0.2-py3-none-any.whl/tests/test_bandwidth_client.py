from requests import Session

from nose.tools import assert_true, assert_list_equal, assert_raises, assert_false, assert_equal, assert_dict_equal
from requests.exceptions import HTTPError
from unittest.mock import patch, Mock

from pybandwidth_v2.bandwidth_client import BandwidthAccountAPI, BandwidthMessagingAPI, BandwidthAPI


class BandwidthClientTestMixin(object):

    """
    Test cases helper
    """
    def _mock_response(
            self,
            status=200,
            content="CONTENT",
            json_data=None,
            raise_for_status=None,
    ):
        """
        since we typically test a bunch of different
        requests calls for a service, we are going to do
        a lot of mock responses, so its usually a good idea
        to have a helper function that builds these things
        """
        mock_resp = Mock()
        # mock raise_for_status call w/optional error
        mock_resp.raise_for_status = Mock()
        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status
        # set status code and content
        mock_resp.status_code = status
        mock_resp.content = content
        # add json data if provided
        if json_data:
            mock_resp.json = Mock(
                return_value=json_data,
            )
        return mock_resp

    @classmethod
    def setup_class(cls):
        cls.mock_session_request_patcher = patch.object(Session, 'request')
        cls.mock_session_request = cls.mock_session_request_patcher.start()
        cls.account_api = BandwidthAccountAPI('test', 'test', 'test')

    @classmethod
    def teardown_class(cls):
        cls.mock_session_request_patcher.stop()


class TestBandwidthAccountAPI(BandwidthClientTestMixin):

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.account_api = BandwidthAccountAPI('test', 'test', 'test')

    @patch.object(BandwidthAPI, '_get')
    def test_search_available_numbers_correctly_set_url_and_params(self, mock_get):
        account_api = BandwidthAccountAPI('test', 'test', 'test')
        numbers = [{
            "key": "value",
        },]
        mock_get.return_value = self._mock_response(json_data=numbers)
        mock_params = {
            'param_key': 'param_value',
        }
        actual_response = account_api.search_available_numbers(**mock_params)

        mock_get.assert_called_once_with(f'accounts/test/availableNumbers', params=mock_params)
        assert_true(mock_get.called)
        assert_false(self.mock_session_request.called)
        assert_equal(actual_response[0]["key"], "value")
        assert_list_equal(numbers, actual_response)

    def test_search_available_numbers_response_ok(self):
        test_numbers = [
            {
                "number": "value",
            },
        ]
        mock_response = self._mock_response(json_data=test_numbers)
        self.mock_session_request.return_value = mock_response

        numbers = self.account_api.search_available_numbers(params={})

        assert_true(self.mock_session_request.called)
        assert_true(mock_response.raise_for_status.called)
        assert_equal(test_numbers[0]["number"], "value")
        assert_list_equal(numbers, test_numbers)

    def test_search_available_numbers_response_not_ok(self):
        mock_response = self._mock_response(status=500, raise_for_status=HTTPError)
        self.mock_session_request.return_value = mock_response

        assert_raises(HTTPError, self.account_api.search_available_numbers, **{})
        assert_true(self.mock_session_request.called)
        assert_true(mock_response.raise_for_status.called)


class TestBandwidthMessagingAPI(BandwidthClientTestMixin):

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.messaging_api = BandwidthMessagingAPI('test', 'test', 'test', 'test')

    @patch.object(BandwidthAPI, '_post')
    def test_send_message_correctly_set_url_and_data(self, mock_post):
        messaging_api = BandwidthMessagingAPI('test', 'test', 'test', 'test')
        success_response = {
            "key": "value",
        }
        mock_post.return_value = success_response
        mock_data = {
            "to": ['123456'],
            "from": '12345',
            "text": 'test',
            "applicationId": 'test',
            "tag": '',
        }
        actual_response = messaging_api.send_message( '12345', ['123456'], 'test')

        mock_post.assert_called_once_with(f'v2/users/test/messages', json=mock_data)
        assert_true(mock_post.called)
        assert_false(self.mock_session_request.called)
        assert_dict_equal(success_response, actual_response)

    def test_send_message_response_ok(self):
        mock_response = self._mock_response()
        self.mock_session_request.return_value = mock_response

        actual_response = self.messaging_api.send_message('12345', ['123456'], 'test')

        assert_true(self.mock_session_request.called)
        assert_true(mock_response.raise_for_status.called)
        assert_equal(200, actual_response.status_code)

    def test_send_message_response_not_ok(self):
        mock_response = self._mock_response(status=500, raise_for_status=HTTPError)
        self.mock_session_request.return_value = mock_response

        assert_raises(HTTPError, self.messaging_api.send_message, '12345', ['123456'], 'test')
        assert_true(self.mock_session_request.called)
        assert_true(mock_response.raise_for_status.called)
