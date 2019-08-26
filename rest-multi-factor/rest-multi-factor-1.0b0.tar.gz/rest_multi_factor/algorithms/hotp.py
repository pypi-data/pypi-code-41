"""Implementation of the HOTP algorithm as defined by RFC 4226."""

__all__ = (
    "HOTPAlgorithm",
)

import hmac
import struct
import hashlib
import warnings


from rest_multi_factor.exceptions import RFCGuidanceWarning
from rest_multi_factor.exceptions import RFCGuidanceException
from rest_multi_factor.algorithms.abstract import AbstractAlgorithm


class HOTPAlgorithm(AbstractAlgorithm):
    """HOTP algorithm implementation."""

    def calculate(self, secret, counter, digits=6, algorithm=hashlib.sha1):
        """
        Calculate a HOTP value.

        Implementation of the HOTP algorithm as defined by
        section 5 of RFC 4226.

        See: https://tools.ietf.org/html/rfc4226#section-5

        :param secret: The shared secret
        :type secret: bytes

        :param counter: The 'moving factor' that is shared between client
                        and server
        :type counter: int

        :param digits: The number of digits for the HOTP value,
        this MUST be at least be 6 digits long

        :param algorithm: The hash algorithm to use,
        should be either sha1, sha256 or sha512
        :type algorithm: function

        :return: The calculated HOTP value
        :rtype: int
        """
        if self.should_validate:
            self.validate(secret, digits)

        packed = struct.pack("!Q", counter)
        result = hmac.new(secret, packed, algorithm).digest()

        modulo = 10 ** digits
        offset = result[19] & 0x0F

        value = (
            (result[offset] & 0x7F) << 24
            | (result[offset+1] & 0xFF) << 16
            | (result[offset+2] & 0xFF) << 8
            | (result[offset+3] & 0xFF)
        )

        return value % modulo

    def validate(self, secret, digits):
        """
        Validate the algorithm requirements.

        These requirements are defined in RFC 4226 section 4.

        See: https://tools.ietf.org/html/rfc4226#section-4

        :param secret: The shared secret
        :type secret: bytes

        :param digits: The number of digits for the HOTP value
        :type digits: int
        """
        if len(secret) < 16:
            raise RFCGuidanceException(
                "The shared secret MUST be at least 128-bits "
                "as defined by 4226 section 4 - requirement 6"
            )

        if len(secret) < 20:
            warnings.warn(
                "RFC 4226 section 4 - requirement 6 RECOMMENDS"
                " that the shared secret is at least 160-bits",
                RFCGuidanceWarning
            )

        if digits < 6:
            raise RFCGuidanceException(
                "The HOTP value MUST be at least be 6-digit value "
                "as defined by RFC 4226 section 4 - requirement 4"
            )

        if digits > 12:
            warnings.warn(
                "The HOTP value MUST be of reasonable length "
                "as defined by RFC 4226 section 4 - requirement 4",
                RFCGuidanceWarning
            )
