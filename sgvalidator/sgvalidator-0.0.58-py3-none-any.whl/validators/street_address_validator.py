import usaddress


class StreetAddressValidator:
    @staticmethod
    def doesAddrHaveNumber(row, config):
        parsed = dict(usaddress.parse(row["street_address"]))
        if "AddressNumber" not in parsed.values():
            return "ADDR_HAS_NO_NUMBER"
        return False

    @staticmethod
    def doesAddrHaveStateNumber(row, config):
        parsed = dict(usaddress.parse(row["street_address"]))
        if "StateName" in parsed.values():
            return "ADDR_CONTAINS_STATE_NAME"
        return False
