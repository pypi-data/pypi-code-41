from src.inspetor.model.inspetor_abstract_model import InspetorAbstractModel
from src.inspetor.model.inspetor_address import InspetorAddress
from src.inspetor.exception.model_exception.inspetor_account_exception import InspetorAccountException


class InspetorAccount(InspetorAbstractModel):
    def __init__(self, address = None, timestamp = None):
        self.id = None
        self.name = None
        self.email = None
        self.document = None
        self.phoneNumber = None
        self.passwordHash = None
        self._address = address
        self._timestamp = timestamp

    def is_valid(self):
        if self.id is None:
            raise InspetorAccountException(
                InspetorAccountException.REQUIRED_ACCOUNT_ID
            )

        if self.email is None:
            raise InspetorAccountException(
                InspetorAccountException.REQUIRED_ACCOUNT_EMAIL
            )

        if self.timestamp is None:
            raise InspetorAccountException(
                InspetorAccountException.REQUIRED_ACCOUNT_TIMESTAMP
            )

        if self.document is None:
            raise InspetorAccountException(
                InspetorAccountException.REQUIRED_ACCOUNT_DOCUMENT
            )

        if self.phoneNumber is None:
            raise InspetorAccountException(
                InspetorAccountException.REQUIRED_ACCOUNT_PHONE_NUMBER
            )

        if self.name is None:
            raise InspetorAccountException(
                InspetorAccountException.REQUIRED_ACCOUNT_PHONE_NUMBER
            )

    def is_valid_update(self):
        if self.id is None:
            raise InspetorAccountException(
                InspetorAccountException.REQUIRED_ACCOUNT_ID
            )

        if self.timestamp is None:
            raise InspetorAccountException(
                InspetorAccountException.REQUIRED_ACCOUNT_TIMESTAMP
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

    #To understand this part, please read https://bit.ly/2ywz8PN
    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        self._timestamp = self.inspetor_date_formatter(timestamp)

    def jsonSerialize(self):
        return {
            "account_id"            : self.encode_data(self.id),
            "account_name"          : self.encode_data(self.name),
            "account_email"         : self.encode_data(self.email),
            "account_document"      : self.encode_data(self.remove_punctuation(self.document)),
            "account_address"       : self.encodeObject(self.address),
            "account_timestamp"     : self.encode_data(self.timestamp),
            "account_phone_number"  : self.encode_data(self.remove_punctuation(self.phoneNumber)),
            "account_password_hash" : self.encode_data(self.passwordHash)
        }