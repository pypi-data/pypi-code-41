import pytest
from datetime import datetime

from src.inspetor.model.inspetor_category import InspetorCategory
from src.inspetor.exception.model_exception.inspetor_category_exception import InspetorCategoryException

class TestInspetorCategory:

    def get_default_category(self):
        category = InspetorCategory()
        category.id = "123"
        category.name = "Category"

        return category

    def test_if_is_valid(self):
        category = self.get_default_category()
        assert category.is_valid() is None