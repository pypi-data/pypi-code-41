from src.inspetor.model.inspetor_abstract_model import InspetorAbstractModel
from src.inspetor.exception.model_exception.inspetor_payment_exception import InspetorPaymentException


class InspetorPayment(InspetorAbstractModel):
    def __init__(self, installments = None, credit_card = None):
        self.id = None
        self.method = None
        self._installments = installments
        self._credit_card = credit_card

    def is_valid(self):
        if self.id is None:
            raise InspetorPaymentException(
                InspetorPaymentException.REQUIRED_PAYMENT_ID
            )

        if self.method is None:
            raise InspetorPaymentException(
                InspetorPaymentException.REQUIRED_PAYMENT_METHOD
            )

        if self.installments is None:
            raise InspetorPaymentException(
                InspetorPaymentException.REQUIRED_PAYMENT_INSTALLMENTS
            )

        self.validate_method()

    def validate_method(self):
        all_methods = [
            "credit_card",
            "boleto",
            "other"
        ]

        if not self.method in all_methods:
            raise InspetorPaymentException(
                InspetorPaymentException.PAYMENT_METHOD_INVALID
            )

        self.validate_credit_card_info()

    def validate_credit_card_info(self):
        if self.method == "credit_card":
            if self.credit_card is None:
                raise InspetorPaymentException(
                    InspetorPaymentException.REQUIRED_PAYMENT_CREDIT_CARD
                )

    #To understand this part, please read https://bit.ly/2ywz8PN
    @property
    def installments(self):
        return self._installments

    @installments.setter
    def installments(self, installments):
        if installments is not None:
            if float(installments) <= 0:
                raise InspetorPaymentException(
                    InspetorPaymentException.REQUIRED_PAYMENT_INSTALLMENTS
                )

        self._installments = installments

    #To understand this part, please read https://bit.ly/2ywz8PN
    @property
    def credit_card(self):
        return self._credit_card

    @credit_card.setter
    def credit_card(self, credit_card):
        if credit_card is not None:
            credit_card.is_valid()

        self._credit_card = credit_card

    def jsonSerialize(self):
        return {
            "payment_instance_id"              : self.encode_data(self.id),
            "payment_instance_method"          : self.encode_data(self.method),
            "payment_instance_installments"    : self.encode_data(self.installments),
            "payment_instance_credit_card_info": self.encodeObject(self.credit_card)
        }

