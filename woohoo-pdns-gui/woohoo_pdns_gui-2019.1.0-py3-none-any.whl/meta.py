# -*- encoding: utf-8 -*-


class LookupDict(dict):
    """
    Dictionary lookup object.

    TODO: understand this...
    https://github.com/kennethreitz/requests/blob/master/requests/structures.py
    """

    def __init__(self, name=None):
        self.name = name
        super(LookupDict, self).__init__()

    def __repr__(self):
        return '<lookup \'%s\'>' % (self.name)

    def __getitem__(self, key):
        # We allow fall-through here, so values default to None

        return self.__dict__.get(key, None)

    def get(self, key, default=None):
        return self.__dict__.get(key, default)


_types = {
    1:  "A",
    2:  "NS",
    5:  "CNAME",
    6:  "SOA",
    12: "PTR",
    15: "MX",
    16: "TXT",
    17: "RP",
    18: "AFSDB",
    24: "SIG",
    25: "KEY",
    28: "AAAA",
    29: "LOC",
    33: "SRV",
    35: "NAPTR",
    36: "KX",
    37: "CERT",
    39: "DNAME",
    42: "APL",
    43: "DS",
    44: "SSHFP",
    45: "IPSECKEY",
    46: "RRSIG",
    47: "NSEC",
    48: "DNSKEY",
    49: "DHCID",
    50: "NSEC3",
    51: "NSEC3PARAM",
    52: "TLSA",
    53: "SMIMEA",
    55: "HIP",
    59: "CDS",
    60: "CDNSKEY",
    61: "OPENPGPKEY",
    249: "TKEY",
    250: "TSIG",
    256: "URI",
    257: "CAA",
    32768: "TA",
    32769: "DLV",
}

# types = dict()
types = LookupDict()


def _init():
    for code, tp in _types.items():
        setattr(types, tp, code)
        setattr(types, "T{}".format(code), tp)


_init()
