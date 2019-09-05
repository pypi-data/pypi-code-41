import pytest
from datetime import datetime

from src.inspetor.model.inspetor_credit_card import InspetorCreditCard
from src.inspetor.model.inspetor_address import InspetorAddress
from src.inspetor.exception.model_exception.inspetor_credit_card_exception import InspetorCreditCardException

class TestInspetorCreditCard:

    def get_default_credit_card(self):
        credit_card = InspetorCreditCard()
        credit_card.first_six_digits = "123456"
        credit_card.last_four_digits = "1234"
        credit_card.holder_name = "Holder Name Test"
        credit_card.holder_cpf = "Holder CPF Test"
        credit_card.billing_address = self.get_default_address()

        return credit_card

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
        ccard = self.get_default_credit_card()
        assert ccard.is_valid() is None