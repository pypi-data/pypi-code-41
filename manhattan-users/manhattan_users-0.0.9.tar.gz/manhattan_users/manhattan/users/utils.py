import flask
from manhattan.forms import validators

__all__ = ['password_validator']


def password_validator(form, field):
    """
    Wrapper for the password validator so that rules for passwords can be
    defined in the applications settings (config).
    """

    return validators.Password(
        **flask.current_app.config['USER_PASSWORD_RULES']
    )(form, field)
