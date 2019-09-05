from src.inspetor.model.inspetor_abstract_model import InspetorAbstractModel
from src.inspetor.exception.model_exception.inspetor_transfer_exception import InspetorTransferException


class InspetorTransfer(InspetorAbstractModel):

    ACCEPTED_STATUS = "accepted"
    REJECTED_STATUS = "rejected"
    PENDING_STATUS  = "pending"

    def __init__(self, timestamp = None):
        self.id = None
        self.item_id = None
        self.sender_account_id = None
        self.receiver_email = None
        self.status = None
        self._timestamp = timestamp

    def is_valid(self):
        if self.id is None:
            raise InspetorTransferException(
                InspetorTransferException.REQUIRED_TRANSFER_ID
            )

        if self.timestamp is None:
            raise InspetorTransferException(
                InspetorTransferException.REQUIRED_TRANSFER_TIMESTAMP
            )

        if self.item_id is None:
            raise InspetorTransferException(
                InspetorTransferException.REQUIRED_TRANSFER_ITEM_ID
            )

        if self.sender_account_id is None:
            raise InspetorTransferException(
                InspetorTransferException.REQUIRED_TRANSFER_ACCOUNT_ID
            )

        if self.receiver_email is None:
            raise InspetorTransferException(
                InspetorTransferException.REQUIRED_TRANSFER_ID_RECEIVER_EMAIL
            )

        self.validate_status()

    def is_valid_update(self):
        if self.id is None:
            raise InspetorTransferException(
                InspetorTransferException.REQUIRED_TRANSFER_ID
            )

        if self.timestamp is None:
            raise InspetorTransferException(
                InspetorTransferException.REQUIRED_TRANSFER_TIMESTAMP
            )

        if self.status is not None:
            self.validate_status()

    def validate_status(self):
        all_status = [
            "accepted",
            "rejected",
            "pending"
        ]

        if not self.status in all_status:
            raise InspetorTransferException(
                InspetorTransferException.TRANSFER_STATUS_INVALID
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
            "transfer_id"               : self.encode_data(self.id),
            "transfer_timestamp" 		: self.encode_data(self.timestamp),
            "transfer_item_id"          : self.encode_data(self.item_id),
            "transfer_sender_account_id": self.encode_data(self.sender_account_id),
            "transfer_receiver_email"   : self.encode_data(self.receiver_email),
            "transfer_status"           : self.encode_data(self.status)
        }





