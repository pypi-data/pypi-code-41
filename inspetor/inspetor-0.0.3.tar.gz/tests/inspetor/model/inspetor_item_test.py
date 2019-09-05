import pytest
from datetime import datetime

from src.inspetor.model.inspetor_item import InspetorItem
from src.inspetor.exception.model_exception.inspetor_item_exception import InspetorItemException


class TestInspetorItem:

    def get_default_item(self):
        item = InspetorItem()
        item.id = "123"
        item.event_id = "123"
        item.session_id = "123"
        item.seating_option = "Seating Option Test"
        item.price = "10"
        item.quantity = "123"

        return item

    def test_if_is_valid(self):
        item = self.get_default_item()
        assert item.is_valid() is None