import pytest
from datetime import datetime

from src.inspetor.model.inspetor_transfer import InspetorTransfer
from src.inspetor.exception.model_exception.inspetor_session_exception import InspetorSessionException


class TestInspetorSession:

    def get_default_transfer(self):
        transfer = InspetorTransfer()
        transfer.id = "123"
        transfer.timestamp = datetime.timestamp(datetime.now())
        transfer.item_id = "123"
        transfer.sender_account_id = "123"
        transfer.receiver_email = "test@email.com"
        transfer.status = "pending"

        return transfer

    def test_if_is_valid(self):
        transfer = self.get_default_transfer()
        assert transfer.is_valid() is None