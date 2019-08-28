import usaddress
from ..types import *


class StreetAddressValidator:
    @staticmethod
    def doesAddrHaveNumber(row, config):
        parsed = dict(usaddress.parse(row["street_address"]))
        if "AddressNumber" not in parsed.values():
            return ValidatorResponse(ValidatorStatus.FAIL, "ADDR_HAS_NO_NUMBER")
        return ValidatorResponse(ValidatorStatus.SUCCESS)

    @staticmethod
    def doesAddrHaveStateName(row, config):
        parsed = dict(usaddress.parse(row["street_address"]))
        if "StateName" in parsed.values():
            return ValidatorResponse(ValidatorStatus.FAIL, "ADDR_CONTAINS_STATE_NAME")
        return ValidatorResponse(ValidatorStatus.SUCCESS)
