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
                "APP_ID":"123",
                "TRACKER_NAME":"123",
                "DEV_ENV":True,
                "INSPETOR_ENV":True
            }
        )
        return inspetor

    def test_track_account_creation(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        account = default_models.get_default_account()

        inspetor.track_account_creation(account)

    def test_track_account_creation_invalid_object(self):
        with pytest.raises(InspetorAccountException):
            default_models = DefaultModels()
            inspetor = self.get_default_inspetor_client()
            account = default_models.get_default_account()
            account.id = None

            inspetor.track_account_creation(account)

    def test_track_account_update(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        account = default_models.get_default_update_account()

        inspetor.track_account_update(account)

    def test_track_account_update_invalid_object(self):
        with pytest.raises(InspetorAccountException):
            default_models = DefaultModels()
            inspetor = self.get_default_inspetor_client()
            account = default_models.get_default_update_account()
            account.id = None

            inspetor.track_account_update(account)

    def test_track_account_deletion(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        account = default_models.get_default_update_account()

        inspetor.track_account_deletion(account)

    def test_track_account_deletion_invalid_object(self):
        with pytest.raises(InspetorAccountException):
            default_models = DefaultModels()
            inspetor = self.get_default_inspetor_client()
            account = default_models.get_default_update_account()
            account.id = None

            inspetor.track_account_deletion(account)

    def test_track_event_creation(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        event = default_models.get_default_event()

        inspetor.track_event_creation(event)

    def test_track_event_creation_object_invalid(self):
        with pytest.raises(InspetorEventException):
            default_models = DefaultModels()
            inspetor = self.get_default_inspetor_client()
            event = default_models.get_default_event()
            event.id = None

            inspetor.track_event_creation(event)

    def test_track_event_update(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        event = default_models.get_default_update_event()

        inspetor.track_event_update(event)

    def test_track_event_update_object_invalid(self):
        with pytest.raises(InspetorEventException):
            default_models = DefaultModels()
            inspetor = self.get_default_inspetor_client()
            event = default_models.get_default_update_event()
            event.id = None

            inspetor.track_event_update(event)

    def test_track_event_deletion(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        event = default_models.get_default_update_event()

        inspetor.track_event_deletion(event)

    def test_track_event_deletion_object_invalid(self):
        with pytest.raises(InspetorEventException):
            default_models = DefaultModels()
            inspetor = self.get_default_inspetor_client()
            event = default_models.get_default_update_event()
            event.id = None

            inspetor.track_event_deletion(event)

    def test_track_login(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        auth = default_models.get_default_auth()

        inspetor.track_login(auth)

    def test_track_login_invalid_object(self):
        with pytest.raises(InspetorAuthException):
            default_models = DefaultModels()
            inspetor = self.get_default_inspetor_client()
            auth = default_models.get_default_auth()
            auth.account_email = None

            inspetor.track_login(auth)

    def test_track_logout(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        auth = default_models.get_default_auth()

        inspetor.track_logout(auth)

    def test_track_logout_invalid_object(self):
        with pytest.raises(InspetorAuthException):
            default_models = DefaultModels()
            inspetor = self.get_default_inspetor_client()
            auth = default_models.get_default_auth()
            auth.account_email = None

            inspetor.track_logout(auth)

    def test_track_sale_creation(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        sale = default_models.get_default_sale()

        inspetor.track_sale_creation(sale)

    def test_track_sale_creation_invalid_object(self):
        with pytest.raises(InspetorSaleException):
            default_models = DefaultModels()
            inspetor = self.get_default_inspetor_client()
            sale = default_models.get_default_sale()
            sale.id = None

            inspetor.track_sale_creation(sale)

    def test_track_sale_update(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        sale = default_models.get_default_update_sale()

        inspetor.track_sale_update(sale)

    def test_track_sale_update_invalid_object(self):
        with pytest.raises(InspetorSaleException):
            default_models = DefaultModels()
            inspetor = self.get_default_inspetor_client()
            sale = default_models.get_default_update_sale()
            sale.id = None

            inspetor.track_sale_update(sale)

    def test_track_password_recovery(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        passw = default_models.get_default_pass_recovery()

        inspetor.track_password_recovery(passw)

    def test_track_password_recovery_invalid_object(self):
        with pytest.raises(InspetorPassRecoveryException):
            default_models = DefaultModels()
            inspetor = self.get_default_inspetor_client()
            passw = default_models.get_default_pass_recovery()
            passw.recovery_email = None

            inspetor.track_password_recovery(passw)

    def test_track_password_reset(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        passw = default_models.get_default_pass_recovery()

        inspetor.track_password_reset(passw)

    def test_track_password_reset_invalid_object(self):
        with pytest.raises(InspetorPassRecoveryException):
            default_models = DefaultModels()
            inspetor = self.get_default_inspetor_client()
            passw = default_models.get_default_pass_recovery()
            passw.recovery_email = None

            inspetor.track_password_reset(passw)

    def test_track_transfer_create(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        transfer = default_models.get_default_transfer()

        inspetor.track_item_transfer_creation(transfer)

    def test_track_transfer_create_invalid_object(self):
        with pytest.raises(InspetorTransferException):
            default_models = DefaultModels()
            inspetor = self.get_default_inspetor_client()
            transfer = default_models.get_default_transfer()
            transfer.id = None

            inspetor.track_item_transfer_creation(transfer)

    def test_track_transfer_update(self):
        default_models = DefaultModels()
        inspetor = self.get_default_inspetor_client()
        transfer = default_models.get_default_transfer()

        inspetor.track_item_transfer_update(transfer)

    def test_track_transfer_update_invalid_object(self):
        with pytest.raises(InspetorTransferException):
            default_models = DefaultModels()
            inspetor = self.get_default_inspetor_client()
            transfer = default_models.get_default_transfer()
            transfer.id = None

            inspetor.track_item_transfer_update(transfer)

    def test_get_inspetor_account(self):
        inspetor = self.get_default_inspetor_client()
        assert type(inspetor.get_inspetor_account()) is InspetorAccount

    def test_get_inspetor_auth(self):
        inspetor = self.get_default_inspetor_client()
        assert type(inspetor.get_inspetor_auth()) is InspetorAuth

    def test_get_inspetor_address(self):
        inspetor = self.get_default_inspetor_client()
        assert type(inspetor.get_inspetor_address()) is InspetorAddress

    def test_get_inspetor_category(self):
        inspetor = self.get_default_inspetor_client()
        assert type(inspetor.get_inspetor_category()) is InspetorCategory

    def test_get_inspetor_credit_card(self):
        inspetor = self.get_default_inspetor_client()
        assert type(inspetor.get_inspetor_credit_card()) is InspetorCreditCard

    def test_get_inspetor_event(self):
        inspetor = self.get_default_inspetor_client()
        assert type(inspetor.get_inspetor_event()) is InspetorEvent

    def test_get_inspetor_pass_recovery(self):
        inspetor = self.get_default_inspetor_client()
        assert type(inspetor.get_inspetor_pass_recovery()) is InspetorPassRecovery

    def test_get_inspetor_payment(self):
        inspetor = self.get_default_inspetor_client()
        assert type(inspetor.get_inspetor_payment()) is InspetorPayment

    def test_get_inspetor_sale(self):
        inspetor = self.get_default_inspetor_client()
        assert type(inspetor.get_inspetor_sale()) is InspetorSale

    def test_get_inspetor_transfer(self):
        inspetor = self.get_default_inspetor_client()
        assert type(inspetor.get_inspetor_transfer()) is InspetorTransfer
