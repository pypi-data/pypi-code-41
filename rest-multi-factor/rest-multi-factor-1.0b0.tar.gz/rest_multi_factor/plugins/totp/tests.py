"""Tests for TOTP logic."""

from rest_framework.test import APITestCase

from rest_multi_factor.algorithms import TOTPAlgorithm
from rest_multi_factor.factories.user import UserFactory
from rest_multi_factor.factories.auth import AuthFactory
from rest_multi_factor.plugins.totp.models import TOTPDevice


class VerificationTests(APITestCase):
    """Tests for TOTP verification implementation."""

    @classmethod
    def setUpTestData(cls):
        """Set up the test data within the test db."""
        cls.user = UserFactory()
        cls.auth = AuthFactory()

        cls.device = TOTPDevice.objects.create(user=cls.user)
        cls.relate = TOTPDevice.challenge.objects.create(
            device=cls.device, token=cls.auth
        )

        cls.algorithm = TOTPAlgorithm()

    def test_successful_verification(self):
        """
        Test a all successful scenario's for TOTP validation.

        Note: when there is a tolerance of 2 there are actually 5
        possibilities 1 and 2 steps before now, now and 1 and 2 steps
        forward. (each step being 30 seconds)
        """
        for i in (-2, -1, 0, 1, 2):

            description = "TOTP not verified for `i={0}`".format(i)
            calculated = self.algorithm.calculate(self.device.secret, drift=i)
            confirmed = self.relate.verify(calculated, save=False)

            self.assertTrue(confirmed, description)

            self.relate.confirm = False

    def test_unsuccessful_verification(self):
        """
        Test all unsuccessful scenario's for TOTP validation.

        Note: Wrong secret value's and such are already tested
        at the algorithm's tests.s
        """
        for i in (-4, -3, 3, 4):
            description = "TOTP verified for `i={0}`".format(i)
            calculated = self.algorithm.calculate(self.device.secret, drift=i)
            confirmed = self.relate.verify(calculated, save=False)

            self.assertFalse(confirmed, description)

            self.relate.confirm = False
