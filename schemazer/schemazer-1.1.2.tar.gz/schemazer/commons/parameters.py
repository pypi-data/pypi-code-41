from schemazer.base import SchemazerParameter
from schemazer.commons.patterns import (PhoneFormat, EmailFormat,
                                        PasswordFormat, SecretKeyFormat,
                                        TokenFormat, ApiKeyFormat)
from schemazer.validator import PatternValidator


class AuthParameters:
    class Phone(SchemazerParameter):
        name = 'phone'
        description = 'Number of phone'
        type = str
        required = True
        example = '81234567890'
        validator = PatternValidator(PhoneFormat)

    class Email(SchemazerParameter):
        name = 'email'
        description = 'Email'
        type = str
        required = True
        example = 'example@gmail.ru'
        validator = PatternValidator(EmailFormat)

    class Password(SchemazerParameter):
        name = 'password'
        description = 'Password'
        type = str
        required = True
        example = 'kf7J73nsIJN'
        validator = PatternValidator(PasswordFormat)

    class SecretKey(SchemazerParameter):
        name = 'secret_key'
        description = 'Secret key parameter'
        type = str
        required = True
        example = '9845121'
        validator = PatternValidator(SecretKeyFormat)

    class Token(SchemazerParameter):
        name = 'token'
        description = 'Registration token'
        type = str
        required = True
        example = '202cb962ac59075b964b07152d234b70'
        validator = PatternValidator(TokenFormat)

    class ApiKey(SchemazerParameter):
        name = 'apikey'
        description = 'Api secret key'
        type = str
        required = True
        example = '202cb962ac59075b'
        validator = PatternValidator(ApiKeyFormat)
