import pytest
from datetime import datetime

from src.inspetor.model.inspetor_address import InspetorAddress
from src.inspetor.exception.model_exception.inspetor_address_exception import InspetorAddressException

class TestInspetorAddress:

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
        address = self.get_default_address()
        assert address.is_valid() is None