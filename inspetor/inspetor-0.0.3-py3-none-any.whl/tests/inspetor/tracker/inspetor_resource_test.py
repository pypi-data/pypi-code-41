from datetime import datetime
import pytest

from src.inspetor_resource import InspetorResource
from tests.inspetor.tracker.default_models import DefaultModels
from src.inspetor.exception.tracker_exception import TrackerException

class TestInspetorResource:
    def get_default_inspetor_resource(self):
        inspetor = InspetorResource(
            {
                "APP_ID":"123",
                "TRACKER_NAME":"123",
                "DEV_ENV":True,
                "INSPETOR_ENV":True
            }
        )
        return inspetor

    def test_track_account_invalid_action(self):
        with pytest.raises(TrackerException):
            default_models = DefaultModels()
            inspetor = self.get_default_inspetor_resource()
            account = default_models.get_default_account()

            inspetor.track_account_action(account, "not_valid")

    def test_track_event_invalid_actiontest_event(self):
        with pytest.raises(TrackerException):
            default_models = DefaultModels()
            inspetor = self.get_default_inspetor_resource()
            event = default_models.get_default_event()

            inspetor.track_event_action(event, "not_valid")

    def test_track_auth_invalid_action(self):
        with pytest.raises(TrackerException):
            default_models = DefaultModels()
            inspetor = self.get_default_inspetor_resource()
            auth = default_models.get_default_auth()

            inspetor.track_account_auth_action(auth, "not_valid")

    def test_track_sale_invalid_action(self):
        with pytest.raises(TrackerException):
            default_models = DefaultModels()
            inspetor = self.get_default_inspetor_resource()
            sale = default_models.get_default_sale()

            inspetor.track_sale_action(sale, "not_valid")

    def test_track_pass_invalid_action(self):
        with pytest.raises(TrackerException):
            default_models = DefaultModels()
            inspetor = self.get_default_inspetor_resource()
            passw = default_models.get_default_pass_recovery()

            inspetor.track_password_recovery_action(passw, "not_valid")

    def test_track_transfer_invalid_action(self):
        with pytest.raises(TrackerException):
            default_models = DefaultModels()
            inspetor = self.get_default_inspetor_resource()
            transfer = default_models.get_default_transfer()

            inspetor.track_item_transfer_action(transfer, "not_valid")

    def test_track_invalid_config(self):
        with pytest.raises(Exception):
            InspetorResource(
                {
                    "APP_ID":None,
                    "TRACKER_NAME":None
                }
            )



