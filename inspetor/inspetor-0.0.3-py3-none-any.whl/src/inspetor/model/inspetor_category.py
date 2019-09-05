from src.inspetor.model.inspetor_abstract_model import InspetorAbstractModel
from src.inspetor.exception.model_exception.inspetor_category_exception import InspetorCategoryException


class InspetorCategory(InspetorAbstractModel):
    def __init__(self):
        self.id = None
        self.name = None

    def is_valid(self):
        if self.id is None:
            raise InspetorCategoryException(
                InspetorCategoryException.REQUIRED_CATEGORY_ID
            )

        if self.name is None:
            raise InspetorCategoryException(
                InspetorCategoryException.REQUIRED_CATEGORY_EMAIL
            )

    def jsonSerialize(self):
        return {
            "category_id"  : self.encode_data(self.id),
            "category_name": self.encode_data(self.name)
        }
