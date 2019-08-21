"""
Module with sanity check functions for the app to run.
"""
from django.core.checks import Error
from django.core.checks import register
from jsmsgr.settings import *


def _assert_required_env_vars_exist():
    """
    Asserts the required env variables exist.
    """
    if SEMAPHORE_SDK_DESTINATION is None:
        return "SEMAPHORE_SDK_DESTINATION env var is required. Maybe you forgot to set it up on the settings file?"

    if USER_API_HOST is None:
        return "USER_API_HOST env var is required. Maybe you forgot to set it up on the settings file?"

    if STOMP_SERVER_HOST is None:
        return "STOMP_SERVER_HOST env var is required. Maybe you forgot to set it up on the settings file?"

    if STOMP_SERVER_PORT is None:
        return "STOMP_SERVER_PORT env var is required. Maybe you forgot to set it up on the settings file?"

    if STOMP_SERVER_USER is None:
        return "STOMP_SERVER_USER env var is required. Maybe you forgot to set it up on the settings file?"

    if STOMP_SERVER_PASSWORD is None:
        return "STOMP_SERVER_PASSWORD env var is required. Maybe you forgot to set it up on the settings file?"

    if STOMP_USE_SSL is None:
        return "STOMP_USE_SSL env var is required. Maybe you forgot to set it up on the settings file?"

    if LISTENER_CLIENT_ID is None:
        return "LISTENER_CLIENT_ID env var is required. Maybe you forgot to set it up on the settings file?"

    if SEMAPHORE_SDK_PUBLISHER_NAME is None:
        return "SEMAPHORE_SDK_PUBLISHER_NAME env var is required. Maybe you forgot to set it up on the settings file?"

    if SEMAPHORE_REPLACEMENT_TAG_USER is None:
        return "SEMAPHORE_REPLACEMENT_TAG_USER env var is required. Maybe you forgot to set it up on the settings file?"


@register()
def sanity_check():
    """
    Checks the required config is present to use the lib.
    """
    errors = []
    error_msg = _assert_required_env_vars_exist()

    errors.append(Error("Missing a required env variable", hint=error_msg, id="jsmsgr"))
