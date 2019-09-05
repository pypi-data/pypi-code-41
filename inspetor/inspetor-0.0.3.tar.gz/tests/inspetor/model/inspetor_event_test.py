import pytest
from datetime import datetime

from src.inspetor.model.inspetor_event import InspetorEvent
from src.inspetor.model.inspetor_address import InspetorAddress
from src.inspetor.model.inspetor_category import InspetorCategory
from src.inspetor.model.inspetor_session import InspetorSession
from src.inspetor.exception.model_exception.inspetor_credit_card_exception import InspetorCreditCardException


class TestInspetorEvent:

    def get_default_category(self):
        category = InspetorCategory()
        category.id = "123"
        category.name = "Category"

        return category

    def get_default_session(self):
        session = InspetorSession()
        session.id = "123"
        session.datetime = int(1562934682)

        return session

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

    def get_default_event(self):
        event = InspetorEvent()
        event.id = "123"
        event.name = "Name Test"
        event.description = "Description Test"
        event.sessions = [
            self.get_default_session()
        ]
        event.status = "private"
        event.slug = "slug-test"
        event.creator_id = "124"
        event.is_physical = True
        event.categories = [
            self.get_default_category()
        ]
        event.address = self.get_default_address()
        event.admins_id = ["123"]
        event.seating_options = ["Seating Option"]
        event.timestamp = datetime.timestamp(datetime.now())

        return event

    def test_if_is_valid(self):
        event = self.get_default_event()
        assert event.is_valid() is None