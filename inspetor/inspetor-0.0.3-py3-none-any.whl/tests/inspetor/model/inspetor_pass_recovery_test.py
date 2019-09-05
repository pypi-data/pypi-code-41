import pytest
from datetime import datetime

from src.inspetor.model.inspetor_pass_recovery import InspetorPassRecovery
from src.inspetor.exception.model_exception.inspetor_pass_recovery_exception import InspetorPassRecoveryException


class TestInspetorPassRecovery:

    def get_default_pass_recovery(self):
        pass_recovery = InspetorPassRecovery()
        pass_recovery.recovery_email = "test@email.com"
        pass_recovery.timestamp = datetime.timestamp(datetime.now())

        return pass_recovery


    def test_if_is_valid(self):
        passreco = self.get_default_pass_recovery()
        assert passreco.is_valid() is None