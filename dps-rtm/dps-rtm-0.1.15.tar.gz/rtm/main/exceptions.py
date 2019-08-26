# --- Standard Library Imports ------------------------------------------------
# None

# --- Third Party Imports -----------------------------------------------------
# None

# --- Intra-Package Imports ---------------------------------------------------
# None


class RTMValidatorError(Exception):
    pass


class RTMValidatorFileError(RTMValidatorError):
    """
    Raise this for any errors related to the excel file itself.
    Examples:
        wrong file extension
        file missing
        missing worksheet
    """
    pass


class UninitializedError(Exception):
    pass


class Uninitialized(RTMValidatorError):
    pass
