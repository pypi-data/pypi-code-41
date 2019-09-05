import pytest
from datetime import datetime

from src.inspetor.model.inspetor_auth import InspetorAuth
from src.inspetor.exception.model_exception.inspetor_auth_exception import InspetorAuthException

class TestInspetorAuth:

    def get_default_auth(self):
        auth = InspetorAuth()
        auth.account_email = "test@email.com"
        auth.account_id = "123"
        auth.timestamp = datetime.timestamp(datetime.now())

        return auth

    def test_if_is_valid(self):
        auth = self.get_default_auth()
        assert auth.is_valid() is None