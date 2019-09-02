"""Provides Currency class."""

from decimal import Decimal


class Currency:
    """Unit of currency."""

    AUD_STR = "AUD"   # Australian Dollar
    CAD_STR = "CAD"   # Canadian Dollar
    CHF_STR = "CHF"   # Swiss Frank
    EUR_STR = "EUR"   # Euro
    GBP_STR = "GBP"   # Great Britain Pound
    JPY_STR = "JPY"   # Japanese Yen
    NZD_STR = "NZD"   # New Zealand Dollar
    USD_STR = "USD"   # United States Dollar

    # These are to be assigned as Currency objects right
    # when this class is initialized.
    AUD = CAD = CHF = EUR = GBP = JPY = NZD = USD = None

    PRECEDENCE = [EUR_STR, GBP_STR, AUD_STR, NZD_STR,
                  USD_STR, CAD_STR, CHF_STR, JPY_STR]
    NAMES = set(PRECEDENCE)

    # Decimal Places
    STANDARD_PLACES = 5
    YEN_PLACES = 3

    # FPU: Number of fractional pips per one unit of this currency
    FPU_STANDARD = 100000
    FPU_REDUCED = 1000

    FIRST_CURRENCY = None
    LAST_CURRENCY = None

    UNITS = {
            #      singular  plural    sign       fractional pips per unit
            AUD_STR: ("dollar", "dollars", u"\x24",   FPU_STANDARD),
            CAD_STR: ("dollar", "dollars", u"\x24",   FPU_STANDARD),
            CHF_STR: ("franc",  "francs",  u"",       FPU_STANDARD),
            EUR_STR: ("euro",   "euros",   u"",       FPU_STANDARD),
            GBP_STR: ("pound",  "pounds",  u"",       FPU_STANDARD),
            JPY_STR: ("yen",    "yen",     u"",       FPU_REDUCED),
            NZD_STR: ("dollar", "dollars", u"\x24",   FPU_STANDARD),
            USD_STR: ("dollar", "dollars", u"\x24",   FPU_STANDARD),
    }
    # Some of these symbols cause printing trouble, so I leave them blank, the
    # swiss frank symbol seems to simply be CHF, so I leave that blank too.

    __currencies = {}  # to hold names to objects.

    @classmethod
    def init_currencies(cls):
        if not cls.__currencies:
            for name in cls.NAMES:
                cls.__currencies[name] = Currency(name)
                setattr(cls, name, cls.__currencies[name])
        cls.FIRST_CURRENCY = cls.__currencies[cls.PRECEDENCE[0]]
        cls.LAST_CURRENCY = cls.__currencies[cls.PRECEDENCE[-1]]

    @classmethod
    def get_list(cls):
        """Get list of currencies in precedence order."""
        return sorted(cls.__currencies.values())

    def __new__(cls, name):
        if isinstance(name, Currency):
            return name
        elif isinstance(name, str):
            name = name.upper().strip()
        currency = cls.__currencies.get(name)
        if currency is not None:
            return currency
        self = object.__new__(cls)
        self.name = name
        try:
            self.singular, self.plural, self.sign, self.fpu = self.UNITS[name]
        except KeyError:
            raise ValueError("Currency not recognized: %s" % name)
        self.precedence = self.PRECEDENCE.index(name) + 1
        self.rounder = Decimal("1") / Decimal(str(self.fpu))
        self.decimal_places = 3 if self.fpu == 5 else False
        return self

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, Currency):
            return NotImplemented
        return self.precedence == other.precedence

    def __lt__(self, other):
        if not isinstance(other, Currency):
            return NotImplemented
        return self.precedence < other.precedence

    def __hash__(self):
        return self.precedence


Currency.init_currencies()
