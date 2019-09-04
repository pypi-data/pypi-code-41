"""HOTP multi factor implementation."""

__all__ = (
    "HOTPDevice",
    "HOTPChallenge",
)

import os
import base64
import binascii
import urllib.parse

from django.db.models.fields import BigIntegerField
from django.db.models.fields.related import CASCADE, ForeignKey

from rest_multi_factor.fields import EncryptedField
from rest_multi_factor.models import Challenge, Device

from rest_multi_factor.settings import multi_factor_settings
from rest_multi_factor.algorithms import HOTPAlgorithm


def _generate_secret():
    return binascii.hexlify(os.urandom(32))


class HOTPDevice(Device):
    """
    HOTP Device implementation.

    Uses the HOTP algorithm to generate a one time password with a
    counter as variable factor.
    """

    secret = EncryptedField(
        max_length=255, editable=False, default=_generate_secret
    )

    counter = BigIntegerField(default=0)

    @property
    def authenticator_url(self):
        """
        Generate a URL for google authenticator.

        This URL could be shared by a QR-code.

        NOTE: According to the wiki are some fields ignored by the current
        version (5.00) of authenticator:

            - digits (on android and blackberry)
            - algorithm

        see: https://github.com/google/google-authenticator/wiki/Key-Uri-Format

        :return: A URI that can be synchronised with google authenticator
        :rtype: str
        """
        label = urllib.parse.quote(self.user.get_username())

        digits = multi_factor_settings.HOTP_DIGITS
        issuer = multi_factor_settings.HOTP_ISSUER
        digest = multi_factor_settings.HOTP_ALGORITHM()

        issuer = urllib.parse.quote(issuer)

        params = urllib.parse.urlencode({
            "issuer": issuer,
            "digits": digits,
            "secret": base64.b32encode(self.secret),
            "counter": self.counter,
            "algorithm": digest.name.upper(),
        })

        return urllib.parse.urlunparse(
            ("otpauth", "hotp", label, None, params, None)
        )


class HOTPChallenge(Challenge):
    """HOTP Challenge, the relation between HOTPDevice and auth token."""

    device = ForeignKey(HOTPDevice, on_delete=CASCADE)
    dispatch = None

    def verify(self, value, save=True):
        """
        Verify a one time password with the HOTP algorithm.

        :param value:: The HOTP token to verify
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

        digits = multi_factor_settings.HOTP_DIGITS
        digest = multi_factor_settings.HOTP_ALGORITHM

        counter = self.device.counter

        algorithm = HOTPAlgorithm()
        tolerance = multi_factor_settings.HOTP_TOLERANCE

        for offset in range(counter, counter + tolerance + 1):
            tryout = algorithm.calculate(
                self.device.secret, offset, digits, digest
            )

            if tryout == value:
                self.confirm = True
                self.device.counter += 1

                if save:
                    self.save()

                return True

        return False
