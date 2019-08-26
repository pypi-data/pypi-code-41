from .types import *
from .validators import *
from .data_preprocessor import DataPreprocessor

validators = [
    {
        "name": "SchemaValidator",
        "announcement": "Checking for schema issues (e.g. required columns, etc.)...",
        "ignorable": False,
        "validatorType": ValidatorTypes.DATAFRAME_VALIDATOR,
        "exitAfterFailure": True,
        "method": SchemaValidator.validateSchema,
        "args": {
            "requiredColumns": {"locator_domain", "location_name", "street_address", "city", "state", "zip",
                                "country_code", "store_number", "phone", "location_type", "latitude", "longitude",
                                "hours_of_operation"}
        }
    },
    {
        "name": "BlankValueChecker",
        "announcement": "Checking for blank cells in your dataset...",
        "ignorable": False,
        "validatorType": ValidatorTypes.DATAFRAME_VALIDATOR,
        "exitAfterFailure": True,
        "method": BlankValueValidator.validateBlankValues
    },
    {
        "name": "CountryCodeFillRateChecker",
        "announcement": "Ensuring that we can infer country code for most of your records...",
        "ignorable": True,
        "validatorType": ValidatorTypes.COLUMN_VALIDATOR,
        "method": FillRateValidator.validateFillRate,
        "columnsToOperateOn": {DataPreprocessor.DETECTED_CC},
        "apology": "We coundn't infer country code on most or all of your data. This might be because your "
                   "geographic columns (city, state, zip) are wrong. Please check to make sure these columns "
                   "in particular look as expected. You may also be receiving this error because you're using a "
                   "strange delimiter in your data, because you have line breaks (\\n) or return characters (\\r), "
                   "etc. If you're receiving this error because most of the data on your store locator is from a "
                   "country other than the US or CA, you may ignore this warning.",
        "args": {
            "MAXIMIUM_PERC_BLANK_ALLOWED": 25
        }
    },
    {
        "name": "GarbageValueValidator",
        "announcement": "Checking for garbage values (HTML tags, nulls, etc.)...",
        "ignorable": False,
        "validatorType": ValidatorTypes.ROW_VALIDATOR,
        "displayCols": [],
        "method": TrashValueValidator.findTrashValues,
        "args": {
            "BAD_TOKENS_INCLUDE": ["null", "<", ">"],
            "BAD_TOKENS_EXCLUDE": ["<MISSING>", "<INACCESSIBLE>"]
        }
    },
    {
        "name": "CentroidValidator",
        "announcement": "Checking for centroid quality issues...",
        "ignorable": True,
        "validatorType": ValidatorTypes.ROW_VALIDATOR,
        "displayCols": ["latitude", "longitude"],
        "method": BadCentroidTagger.tag,
        "args": {
            "MINIMUM_NUMBER_SIGNIFICANT_DIGITS_FOR_LAT_LNG": 2
        }
    },
    {
        "name": "StreetAddressHasNumber",
        "announcement": "Ensuring that all street addresses have an address number...",
        "ignorable": True,
        "validatorType": ValidatorTypes.ROW_VALIDATOR,
        "displayCols": ["street_address"],
        "countryFilter": CountryCode.US,
        "method": StreetAddressValidator.doesAddrHaveNumber
    },
    {
        "name": "StreetAddressHasStateName",
        "announcement": "Ensuring that street addresses do not have a state name in them...",
        "ignorable": True,
        "validatorType": ValidatorTypes.ROW_VALIDATOR,
        "displayCols": ["street_address"],
        "countryFilter": CountryCode.US,
        "method": StreetAddressValidator.doesAddrHaveStateName
    },
    {
        "name": "GeoConsistencyValidator",
        "announcement": "Validating consistency of geography columns...",
        "ignorable": True,
        "validatorType": ValidatorTypes.ROW_VALIDATOR,
        "displayCols": ["zip", "state"],
        "countryFilter": CountryCode.US,
        "method": GeoConsistencyValidator.getBadGeoConsistencyReason
    },
    {
        "name": "CountryValidator",
        "announcement": "Validating country-specific information (states, zip codes, phone #'s)...",
        "ignorable": False,
        "validatorType": ValidatorTypes.ROW_VALIDATOR,
        "displayCols": ["state", "phone", "zip"],
        "method": CountryValidator.validateCountrySpecificValues
    },
    {
        "name": "StoreNumberColumnValidator",
        "announcement": "Ensuring that store number column is totally filled and unique or totally empty...",
        "ignorable": True,
        "validatorType": ValidatorTypes.COLUMN_VALIDATOR,
        "method": StoreNumberColumnValidator.validateStoreNumberColumn,
        "columnsToOperateOn": {"store_number"}
    },
    {
        "name": "CountValidator",
        "announcement": "Checking the number of POI in your data against our internal truthset...",
        "ignorable": True,
        "validatorType": ValidatorTypes.DATAFRAME_VALIDATOR,
        "countryFilter": CountryCode.US,
        "method": CountValidator.validatePoiCountAgainstRawCount,
        "args": {
            "MAXIMUM_COUNT_DIFF_THRESHOLD":  5,
            "MAXIMUM_PERC_DIFF_THRESHOLD": 10.0
        }
    },
    {
        "name": "FillRateValidator",
        "announcement": "Checking that each column has adequate fill rate...",
        "warnOnly": True,
        "validatorType": ValidatorTypes.COLUMN_VALIDATOR,
        "method": FillRateValidator.validateFillRate,
        "columnsToOperateOn": {"locator_domain", "location_name", "street_address", "city", "state", "zip",
                               "country_code", "store_number", "phone", "location_type", "latitude", "longitude",
                               "hours_of_operation"},
        "args": {
            "MAXIMIUM_PERC_BLANK_ALLOWED": 40
        }
    },
    {
        "name": "IdentityDuplicationValidator",
        "announcement": "Checking for duplicate identity rows...",
        "ignorable": False,
        "validatorType": ValidatorTypes.DATAFRAME_VALIDATOR,
        "method": DuplicationValidator.validateIdentityDuplicates,
        "args": {
            "IDENTITY_KEYS": ["location_name", "street_address", "city", "state", "zip", "country_code",
                              "location_type"],
        }
    },
    {
        "name": "LatLngDuplicationValidator",
        "announcement": "Checking for <lat, lngs> with multiple addressess...",
        "ignorable": True,
        "validatorType": ValidatorTypes.DATAFRAME_VALIDATOR,
        "method": DuplicationValidator.validateLatLngDuplicates
    },
    {
        "name": "AddrWithMultipleCoordinatesValidator",
        "announcement": "Checking for addresses that have multiple <lat, lngs> associated with them...",
        "warnOnly": True,
        "validatorType": ValidatorTypes.DATAFRAME_VALIDATOR,
        "method": DuplicationValidator.getAddrsWithMultipleLatLngs
    },
]
