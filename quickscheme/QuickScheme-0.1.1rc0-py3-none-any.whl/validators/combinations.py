''' Combinations of Validations '''


def validate_all(*validators):
    ''' 
    Logical "AND" - Must Match All Validators listed


    '''
    def validator(field_value):
        for validator in validators:
            if not validator(field_value):
                return False
        return True

    return validator


def validate_any(*validators):
    ''' 
    Logical "OR" - Must Match at least one of the Validators listed

    '''
    def validator(field_value):
        for validator in validators:
            if validator(field_value):
                return True
        return False

    return validator
