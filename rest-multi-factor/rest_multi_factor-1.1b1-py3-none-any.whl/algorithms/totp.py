"""TOTP Algorithm as described by RFC 6238."""

__all__ = (
    "TOTPAlgorithm",
)

import time
import hashlib


from rest_multi_factor.algorithms.hotp import HOTPAlgorithm


class TOTPAlgorithm(HOTPAlgorithm):
    """
    TOTP Algorithm as described by RFC 6238.

    This algorithm extends the HOTP algorithm in such a way that the
    counter is provided by the number of 'steps' that fit in a time
    range from 'time zero' or 'T0' until the current time.

    Because the number of steps will change after the time span of a
    step (e.g. 30 seconds for every step), will the HOTP value also
    change (every 30 seconds) without the secret that changes.
    """

    def calculate(self, secret, step=30, time_zero=0, digits=6, drift=0,
                  algorithm=hashlib.sha1):
        """
        Calculate a TOTP value.

        This is basically a extension of the HOTP algorithm.

        :param secret: The secret that will be encoded to a TOTP value
        :type secret: bytes

        :param step: The number of seconds within a step
        :type step: int

        :param time_zero: The start time to count the number of steps from.
        :type time_zero: int

        :param digits: The number of digits that the TOPT value will have
        :type digits: int

        :param drift: The drift that is to be used. This can be used for
        validation to get a TOTP value of a number of steps forward or back
        :type drift: int

        :param algorithm: The hash algorithm to use, should be either sha1,
        sha256 or sha512
        :type algorithm: function

        :return: The encoded secret (The TOTP value)
        :rtype: int
        """
        calculated = self.calculate_step(time_zero, step, drift)
        return HOTPAlgorithm.calculate(
            self, secret, calculated, digits, algorithm
        )

    @staticmethod
    def calculate_step(time_zero, step, drift):
        """
        Calculate the number of steps, this will serve as the HOTP counter.

        :param time_zero: The start time to count the number of steps from
        :type time_zero: int

        :param step: The number of seconds within a single step
        :type step: int

        :param drift: The drift that is to be used. This can be used for
        validation to get a TOTP value of a number of steps forward or back
        :type drift: int

        :return: The number of steps within the time range from time zero (T0)
                 until the current time.
        """
        return ((int(time.time()) - time_zero) // step) + drift
