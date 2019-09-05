from src.inspetor.model.inspetor_abstract_model import InspetorAbstractModel
from src.inspetor.exception.model_exception.inspetor_credit_card_exception import InspetorCreditCardException


class InspetorCreditCard(InspetorAbstractModel):

    CREDIT_CARD  = "credit_card"
    BOLETO       = "boleto"
    OTHER_METHOD = "other"

    def __init__(self):
        self.first_six_digits = None
        self.last_four_digits = None
        self.holder_name = None
        self.holder_cpf = None
        self.billing_address = None

    def is_valid(self):
        if self.first_six_digits is None:
            raise InspetorCreditCardException(
                InspetorCreditCardException.REQUIRED_CREDIT_CARD_SIX
            )

        if self.last_four_digits is None:
            raise InspetorCreditCardException(
                InspetorCreditCardException.REQUIRED_CREDIT_CARD_FOUR
            )

        if self.holder_name is None:
            raise InspetorCreditCardException(
                InspetorCreditCardException.REQUIRED_CREDIT_CARD_HOLDER_NAME
            )

        if self.holder_cpf is None:
            raise InspetorCreditCardException(
                InspetorCreditCardException.REQUIRED_CREDIT_CARD_HOLDER_CPF
            )

        if self.billing_address is None:
            raise InspetorCreditCardException(
                InspetorCreditCardException.REQUIRED_CREDIT_CARD_ADDRESS
            )

    #To understand this part, please read https://bit.ly/2ywz8PN
    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, address):
        if address is not None:
            address.is_valid()

        self._address = address

    def jsonSerialize(self):
        return {
            "cc_first_six"      : self.encode_data(self.first_six_digits),
            "cc_last_four"      : self.encode_data(self.last_four_digits),
            "cc_holder_name"    : self.encode_data(self.holder_name),
            "cc_holder_cpf"     : self.encode_data(self.holder_cpf),
            "cc_billing_address": self.encodeObject(self.billing_address)
        }