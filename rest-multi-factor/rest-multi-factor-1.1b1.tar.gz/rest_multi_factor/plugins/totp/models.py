"""TOTP multi factor implementation."""

__all__ = (
    "TOTPDevice",
    "TOTPChallenge",
)

import os
import base64
import binascii
import urllib.parse

from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey

from rest_multi_factor.fields import EncryptedField
from rest_multi_factor.models import Device, Challenge
from rest_multi_factor.settings import multi_factor_settings
from rest_multi_factor.algorithms.totp import TOTPAlgorithm


def _generate_secret():
    return binascii.hexlify(os.urandom(32))


class TOTPDevice(Device):
    """
    TOTP device implementation.

    Uses the TOTP algorithm to generate a new one time password
    every 30 seconds (by default).
    """

    secret = EncryptedField(
        max_length=255, editable=False, default=_generate_secret
    )

    @property
    def authenticator_url(self):
        """
        Generate a URL for google authenticator.

        This URL could be shared by a QR-code.

        NOTE: According to the wiki are some fields ignored by the current
        version (5.00) of authenticator:

            - digits (on android and blackberry)
            - period
            - algorithm

        see: https://github.com/google/google-authenticator/wiki/Key-Uri-Format

        :return: A URI that can be synchronised with google authenticator
        :rtype: str
        """
        label = urllib.parse.quote(self.user.get_username())

        period = multi_factor_settings.TOTP_PERIOD
        issuer = multi_factor_settings.TOTP_ISSUER
        digits = multi_factor_settings.TOTP_DIGITS
        digest = multi_factor_settings.TOTP_ALGORITHM()

        issuer = urllib.parse.quote(issuer)

        params = urllib.parse.urlencode({
            "issuer": issuer,
            "digits": digits,
            "period": period,
            "secret": base64.b32encode(self.secret),
            "algorithm": digest.name.upper(),
        })

        return urllib.parse.urlunparse(
            ("otpauth", "totp", label, None, params, None)
        )


class TOTPChallenge(Challenge):
    """
    TOTP Challenge implementation.

    Acts as a relation between the TOTP device and the auth token.
    """

    device = ForeignKey(TOTPDevice, on_delete=CASCADE, editable=False)
    dispatch = None

    def verify(self, value, save=True):
        """
        Validate a token to check if this challenge can be confirmed.

        :param value: The TOTP token to verify
        :type value: str | int

        :param save: Whether to save the result or not
        :type save: bool

        :return: Whether this token is valid or not
        :rtype: bool
        """
        if self.confirm:  # noqa: no cover
            raise RuntimeError("This challenge is already confirmed")

        try:
            value = int(value)

        except (TypeError, ValueError):  # noqa: no cover
            return False

        period = multi_factor_settings.TOTP_PERIOD
        digits = multi_factor_settings.TOTP_DIGITS
        digest = multi_factor_settings.TOTP_ALGORITHM

        algorithm = TOTPAlgorithm()
        tolerance = multi_factor_settings.TOTP_TOLERANCE

        for offset in range(-tolerance, tolerance+1):
            tryout = algorithm.calculate(
                self.device.secret, period, 0, digits, offset, digest
            )

            if tryout == value:
                self.confirm = True
                if save:
                    self.save()

                return True

        return False
