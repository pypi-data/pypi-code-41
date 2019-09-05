from src.inspetor.model.inspetor_abstract_model import InspetorAbstractModel
from src.inspetor.exception.model_exception.inspetor_pass_recovery_exception import InspetorPassRecoveryException


class InspetorPassRecovery(InspetorAbstractModel):
    def __init__(self, timestamp = None):
        self.recovery_email = None
        self._timestamp = timestamp

    def is_valid(self):
        if self.recovery_email is None:
            raise InspetorPassRecoveryException(
                InspetorPassRecoveryException.REQUIRED_PASS_RECOVERY_EMAIL
            )

        if self.timestamp is None:
            raise InspetorPassRecoveryException(
                InspetorPassRecoveryException.REQUIRED_PASS_RECOVERY_TIMESTAMP
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
            "pass_recovery_email"    : self.encode_data(self.recovery_email),
            "pass_recovery_timestamp": self.encode_data(self.timestamp)
        }