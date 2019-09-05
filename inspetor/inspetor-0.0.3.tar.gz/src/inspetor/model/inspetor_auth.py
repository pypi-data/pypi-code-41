from src.inspetor.model.inspetor_abstract_model import InspetorAbstractModel
from src.inspetor.exception.model_exception.inspetor_auth_exception import InspetorAuthException

class InspetorAuth(InspetorAbstractModel):
    def __init__(self, timestamp = None):
        self.account_email = None
        self.account_id = None
        self._timestamp = timestamp

    def is_valid(self):
        if self.account_email is None:
            raise InspetorAuthException(
                InspetorAuthException.REQUIRED_AUTH_EMAIL
            )

        if self.timestamp is None:
            raise InspetorAuthException(
                InspetorAuthException.REQUIRED_AUTH_TIMESTAMP
            )

    #To understand this part, please read https://bit.ly/2ywz8PN
    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        self._timestamp = self.inspetor_date_formatter(timestamp)

    def jsonSerialize(self):
        return {
            "auth_account_email" : self.encode_data(self.account_email),
            "auth_timestamp"     : self.encode_data(self.timestamp),
            "auth_account_id"     : self.encode_data(self.account_id)
        }