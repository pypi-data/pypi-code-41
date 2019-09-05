import pytest
from datetime import datetime

from src.inspetor.model.inspetor_account import InspetorAccount
from src.inspetor.model.inspetor_address import InspetorAddress
from src.inspetor.exception.model_exception.inspetor_account_exception import InspetorAccountException

class TestInspetorAccount:

    def get_default_account(self):
        account = InspetorAccount()
        account.id = "123"
        account.name = "Test"
        account.email = "test@email.com"
        account.document = "12312312312"
        account.phoneNumber = "112345678"
        account.address = self.get_default_address()
        account.timestamp = datetime.timestamp(datetime.now())

        return account

    def get_default_address(self):
        address = InspetorAddress()
        address.street = "Test Stree"
        address.number = "123"
        address.zip_code = "123456"
        address.city = "Test City"
        address.state = "Test State"
        address.country = "Test Country"
        address.latitude = "123"
        address.longitude = "123"

        return address

    def test_if_is_valid(self):
        account = self.get_default_account()
        assert account.is_valid() is None