''' String FieldValue Validators '''


#from .combinations import validate_all, validate_any
from .common import failure


def minmax_validator(min_value=None, max_value=None):
    '''
    Validate number based on minumum and maximum value
    '''

    def validator(field_value):
        ''' Validator '''
        value = field_value.get()
        if min_value is not None and value < min_value:
            return failure(field_value, "Value must be at least %s, got %s", min_value, value)
        if max_value is not None and value > max_value:
            return failure(field_value, "Value must be at most %s, got %s", max_value, value)
        return True

    return validator
