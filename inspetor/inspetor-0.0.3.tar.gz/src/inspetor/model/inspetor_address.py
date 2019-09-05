from src.inspetor.model.inspetor_abstract_model import InspetorAbstractModel
from src.inspetor.exception.model_exception.inspetor_address_exception import InspetorAddressException

class InspetorAddress(InspetorAbstractModel):
    def __init__(self):
        self.street = None
        self.number = None
        self.zip_code = None
        self.city = None
        self.state = None
        self.country = None
        self.latitude = None
        self.longitude = None

    def is_valid(self):
        if self.street is None:
            raise InspetorAddressException(
                InspetorAddressException.REQUIRED_ADDRESS_STREET
            )

        if self.zip_code is None:
            raise InspetorAddressException(
                InspetorAddressException.REQUIRED_ADDRESS_ZIPCODE
            )

        if self.city is None:
            raise InspetorAddressException(
                InspetorAddressException.REQUIRED_ADDRESS_CITY
            )

        if self.state is None:
            raise InspetorAddressException(
                InspetorAddressException.REQUIRED_ADDRESS_STATE
            )

        if self.country is None:
            raise InspetorAddressException(
                InspetorAddressException.REQUIRED_ADDRESS_COUNTRY
            )

    def jsonSerialize(self):
        return {
            "address_street"   : self.encode_data(self.street),
            "address_number"   : self.encode_data(self.number),
            "address_zip_code" : self.encode_data(self.zip_code),
            "address_city"     : self.encode_data(self.city),
            "address_state"    : self.encode_data(self.state),
            "address_country"  : self.encode_data(self.country),
            "address_latitude" : self.encode_data(self.latitude),
            "address_longitude": self.encode_data(self.longitude)
        }
