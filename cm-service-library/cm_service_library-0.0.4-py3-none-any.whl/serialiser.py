class RequiredFieldException(Exception):
    pass


class Rule(object):

    def __init__(self, **kwargs):
        self.required = kwargs.get('required', False)


class Serialiser(object):

    fields = []
    validation = {}
    validated = False

    def validate(self):
        for field in self.fields:
            field_data = getattr(self, field, None)

            if field in self.validation:
                for rule in self.validation.get(field):

                    # Required
                    if rule.required and (field_data is None or field_data == ''):
                        raise RequiredFieldException("`{field}` is required and must not be null or blank.")

        self.validated = True
        return True
