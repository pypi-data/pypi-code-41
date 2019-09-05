from src.inspetor.model.inspetor_abstract_model import InspetorAbstractModel
from src.inspetor.model.inspetor_item import InspetorItem
from src.inspetor.exception.model_exception.inspetor_sale_exception import InspetorSaleException


class InspetorSale(InspetorAbstractModel):

    ACCEPTED_STATUS        = "accepted"
    DECLINED_STATUS        = "declined"
    PENDING_STATUS         = "pending"
    REFUNDED_STATUS        = "refunded"
    MANUAL_ANALYSIS_STATUS = "manual_analysis"

    def __init__(self, timestamp = None, items = None, payment = None):
        self.id = None
        self.account_id = None
        self.total_value = None
        self.status = None
        self.is_fraud = None
        self.analyzed_by = None
        self._timestamp = timestamp
        self._items = items
        self._payment = payment

    def is_valid(self):
        if self.id is None:
            raise InspetorSaleException(
                InspetorSaleException.REQUIRED_SALE_ID
            )

        if self.account_id is None:
            raise InspetorSaleException(
                InspetorSaleException.REQUIRED_SALE_ACCOUNT_ID
            )

        if self.status is None:
            raise InspetorSaleException(
                InspetorSaleException.REQUIRED_SALE_STATUS
            )

        self.validate_status()

        if self.timestamp is None:
            raise InspetorSaleException(
                InspetorSaleException.REQUIRED_SALE_TIMESTAMP
            )

        if self.items is None or self.items == []:
            raise InspetorSaleException(
                InspetorSaleException.REQUIRED_SALE_ITEMS
            )

        if self.payment is None:
            raise InspetorSaleException(
                InspetorSaleException.REQUIRED_SALE_PAYMENT
            )

        self.set_total_value()

    def is_valid_update(self):
        if self.id is None:
            raise InspetorSaleException(
                InspetorSaleException.REQUIRED_SALE_ID
            )

        if self.timestamp is None:
            raise InspetorSaleException(
                InspetorSaleException.REQUIRED_SALE_TIMESTAMP
            )

        if self.status is not None:
            self.validate_status()

        if self.is_fraud is None:
            raise InspetorSaleException(
                InspetorSaleException.REQUIRED_SALE_IS_FRAUD
            )

        if self.analyzed_by is None:
            raise InspetorSaleException(
                InspetorSaleException.REQUIRED_SALE_ANALYZED_BY
            )

    def validate_status(self):
        all_status = [
            "accepted",
            "declined",
            "pending",
            "refunded",
            "manual_analysis"
        ]

        if not self.status in all_status:
            raise InspetorSaleException(
                InspetorSaleException.SALE_STATUS_INVALID
            )

    def set_total_value(self):
        for item in self.items:
            try:
                self.total_value += str(float(item.price)*float(item.quantity))
            except:
                raise InspetorSaleException(
                    InspetorSaleException.SALE_ITEM_PRICE_INVALID
                )

    #To understand this part, please read https://bit.ly/2ywz8PN
    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, items):
        if items is not None:
            for item in items:
                item.is_valid()

        self._items = items

    #To understand this part, please read https://bit.ly/2ywz8PN
    @property
    def payment(self):
        return self._payment

    @payment.setter
    def payment(self, payment):
        if payment is not None:
            self._payment = payment.is_valid()

        self._payment = payment

    #To understand this part, please read https://bit.ly/2ywz8PN
    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        self._timestamp = self.inspetor_date_formatter(timestamp)

    def jsonSerialize(self):
        return {
            "sale_id"               : self.encode_data(self.id),
            "sale_account_id"       : self.encode_data(self.account_id),
            "sale_total_value"      : self.encode_data(self.total_value),
            "sale_status"           : self.encode_data(self.status),
            "sale_is_fraud"         : self.encode_data(self.is_fraud),
            "sale_analyzed_by"      : self.encode_data(self.analyzed_by),
            "sale_timestamp"  		: self.encode_data(self._timestamp),
            "sale_items"            : self.encode_array(self._items, True),
            "sale_payment_instance" : self.encodeObject(self._payment)
        }

