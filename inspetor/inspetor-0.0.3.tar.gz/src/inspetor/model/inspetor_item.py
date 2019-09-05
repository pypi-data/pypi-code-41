from src.inspetor.model.inspetor_abstract_model import InspetorAbstractModel
from src.inspetor.exception.model_exception.inspetor_item_exception import InspetorItemException


class InspetorItem(InspetorAbstractModel):
    def __init__(self, price = None, quantity = None):
        self.id = None
        self.event_id = None
        self.session_id = None
        self.seating_option = None
        self._price = price
        self._quantity = quantity

    def is_valid(self):
        if self.id is None:
            raise InspetorItemException(
                InspetorItemException.REQUIRED_ITEM_ID
            )

        if self.event_id is None:
            raise InspetorItemException(
                InspetorItemException.REQUIRED_ITEM_EVENT_ID
            )

        if self.session_id is None:
            raise InspetorItemException(
                InspetorItemException.REQUIRED_ITEM_SESSION_ID
            )

        if self._price is None:
            raise InspetorItemException(
                InspetorItemException.REQUIRED_ITEM_PRICE
            )

        if self._quantity is None:
            raise InspetorItemException(
                InspetorItemException.REQUIRED_ITEM_QUANTITY
            )


    #To understand this part, please read https://bit.ly/2ywz8PN
    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, price):
        if float(price) < 0.0:
            raise InspetorItemException(
                InspetorItemException.ITEM_PRICE_INVALID
            )

        self._price = price

    #To understand this part, please read https://bit.ly/2ywz8PN
    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, quantity):
        if float(quantity) <= 0:
            raise InspetorItemException(
                InspetorItemException.REQUIRED_ITEM_QUANTITY
            )

        self._quantity = quantity

    def jsonSerialize(self):
        return {
            "item_id"            : self.encode_data(self.id),
            "item_event_id"      : self.encode_data(self.event_id),
            "item_session_id"    : self.encode_data(self.session_id),
            "item_price"         : self.encode_data(self.price),
			"item_seating_option": self.encode_data(self.seating_option),
			"item_quantity"      : self.encode_data(self.quantity)
        }
