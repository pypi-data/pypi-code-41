from schemazer import RequestErrors
from schemazer.base import SchemazerMethod
from schemazer.commons.errors import AuthErrors
from schemazer.commons.limits import AllLimit
from schemazer.commons.parameters import AuthParameters


class TestMethodsGroup:
    _name = 'auth'
    test_method = SchemazerMethod(
        name='test_method',
        description='Test method',
        parameters=[
            AuthParameters.Email(),
        ],
        errors=[RequestErrors.BadRequest,
                AuthErrors.UserNotFound],
        limits=[AllLimit()]
    )


class TestSchema:
    test = TestMethodsGroup
