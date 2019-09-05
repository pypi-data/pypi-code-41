from datetime import datetime
import pytest

from src.inspetor_client import InspetorClient
from tests.inspetor.tracker.default_models import DefaultModels
from src.inspetor.model.inspetor_account import InspetorAccount
from src.inspetor.model.inspetor_address import InspetorAddress
from src.inspetor.model.inspetor_category import InspetorCategory
from src.inspetor.model.inspetor_credit_card import InspetorCreditCard
from src.inspetor.model.inspetor_auth import InspetorAuth
from src.inspetor.model.inspetor_event import InspetorEvent
from src.inspetor.model.inspetor_pass_recovery import InspetorPassRecovery
from src.inspetor.model.inspetor_payment import InspetorPayment
from src.inspetor.model.inspetor_sale import InspetorSale
from src.inspetor.model.inspetor_transfer import InspetorTransfer
from src.inspetor.exception.tracker_exception import TrackerException
from src.inspetor.exception.model_exception.inspetor_auth_exception import InspetorAuthException
from src.inspetor.exception.model_exception.inspetor_sale_exception import InspetorSaleException
from src.inspetor.exception.model_exception.inspetor_account_exception import InspetorAccountException
from src.inspetor.exception.model_exception.inspetor_event_exception import InspetorEventException
from src.inspetor.exception.model_exception.inspetor_pass_recovery_exception import InspetorPassRecoveryException
from src.inspetor.exception.model_exception.inspetor_transfer_exception import InspetorTransferException

class TestInspetorClient:
    def get_default_inspetor_client(self):
        inspetor = InspetorClient(
            {
                "APP_ID": "123",
                "TRACKER_NAME": "inspetor.python.test",
                "DEV_ENV": True,
                "INSPETOR_ENV": False
            }
        )
        return inspetor

    def test_track_account_creation(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        account = default_models.get_default_account()

        inspetor.track_account_creation(account)

    def test_track_account_update(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        account = default_models.get_default_update_account()

        inspetor.track_account_update(account)

    def test_track_account_deletion(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        account = default_models.get_default_update_account()

        inspetor.track_account_deletion(account)

    def test_track_event_creation(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        event = default_models.get_default_event()

        inspetor.track_event_creation(event)

    def test_track_event_update(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        event = default_models.get_default_update_event()

        inspetor.track_event_update(event)

    def test_track_event_deletion(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        event = default_models.get_default_update_event()

        inspetor.track_event_deletion(event)

    def test_track_login(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        auth = default_models.get_default_auth()

        inspetor.track_login(auth)

    def test_track_logout(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        auth = default_models.get_default_auth()

        inspetor.track_logout(auth)

    def test_track_sale_creation(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        sale = default_models.get_default_sale()

        inspetor.track_sale_creation(sale)

    def test_track_sale_update(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        sale = default_models.get_default_update_sale()

        inspetor.track_sale_update(sale)

    def test_track_password_recovery(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        passw = default_models.get_default_pass_recovery()

        inspetor.track_password_recovery(passw)

    def test_track_password_reset(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        passw = default_models.get_default_pass_recovery()

        inspetor.track_password_reset(passw)

    def test_track_transfer_create(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        transfer = default_models.get_default_transfer()

        inspetor.track_item_transfer_creation(transfer)

    def test_track_transfer_update(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        transfer = default_models.get_default_transfer()

        inspetor.track_item_transfer_update(transfer)