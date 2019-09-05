import pytest
from datetime import datetime

from src.inspetor.model.inspetor_session import InspetorSession
from src.inspetor.exception.model_exception.inspetor_session_exception import InspetorSessionException


class TestInspetorSession:

    def get_default_session(self):
        session = InspetorSession()
        session.id = "123"
        session.datetime = int(1562934682)

        return session

    def test_if_is_valid(self):
        session = self.get_default_session()
        assert session.is_valid() is None