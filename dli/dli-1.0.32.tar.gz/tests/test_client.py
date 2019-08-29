from http import HTTPStatus
from unittest import TestCase, mock

from requests import Session

from dli.client.auth import AuthenticationFailure, get_auth_key


class TestAuth(TestCase):

    @mock.patch.object(Session, 'post')
    def test_handle_auth_error(self, post):
        text = 'Some server error message'
        post.return_value = mock.Mock(status_code=HTTPStatus.UNAUTHORIZED, text=text)
        with self.assertRaises(AuthenticationFailure) as cm:
            get_auth_key('api-key', 'api-root')

        self.assertEqual(str(cm.exception), text)

    @mock.patch.object(Session, 'post')
    def test_handle_auth_error_for_403_response(self, post):
        """
        Should show a generic response message
        """
        post.return_value = mock.Mock(status_code=HTTPStatus.FORBIDDEN)
        with self.assertRaises(AuthenticationFailure) as cm:
            get_auth_key('api-key', 'api-root')
            
        exception_message = str(cm.exception)
        self.assertIn(AuthenticationFailure.GENERIC_ERROR_MESSAGE, exception_message)
        self.assertIn('api-root', exception_message)

    @mock.patch.object(Session, 'post')
    def test_auth_error_for_unknown_auth_error(self, post):
        """
        Should show a generic response message if no error message
        """
        post.return_value = mock.Mock(status_code=HTTPStatus.UNAUTHORIZED, text='')

        with self.assertRaises(AuthenticationFailure) as cm:
            get_auth_key('api-key', 'api-root')

        self.assertEqual(
            str(cm.exception),
            AuthenticationFailure.GENERIC_ERROR_MESSAGE
        )
