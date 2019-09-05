
from src.inspetor.model.inspetor_abstract_model import InspetorAbstractModel
from src.inspetor.model.inspetor_account import InspetorAccount
from src.inspetor.model.inspetor_address import InspetorAddress
from src.inspetor.model.inspetor_auth import InspetorAuth
from src.inspetor.model.inspetor_category import InspetorCategory
from src.inspetor.model.inspetor_credit_card import InspetorCreditCard
from src.inspetor.model.inspetor_event import InspetorEvent
from src.inspetor.model.inspetor_item import InspetorItem
from src.inspetor.model.inspetor_pass_recovery import InspetorPassRecovery
from src.inspetor.model.inspetor_payment import InspetorPayment
from src.inspetor.model.inspetor_sale import InspetorSale
from src.inspetor.model.inspetor_session import InspetorSession
from src.inspetor.model.inspetor_transfer import InspetorTransfer
from src.inspetor_resource import InspetorResource


class InspetorClient:
    def __init__(self, configDict):
        """
        Initialize service
        """
        try:
            self.inspetor_resource = InspetorResource(configDict)
        except Exception:
            raise

    def track_sale_creation(self, sale):
        """
        Track Sale creation
        """
        try:
            self.inspetor_resource.track_sale_action(
                sale,
                "sale_create"
            )
        except Exception:
            raise

        return True

    def track_sale_update(self, sale):
        """
        Track Sale update
        """
        try:
            self.inspetor_resource.track_sale_action(
                sale,
                "sale_update"
            )
        except Exception:
            raise

        return True

    def track_account_creation(self, account):
        """
        Track Account creation
        """
        try:
            self.inspetor_resource.track_account_action(
                account,
                "account_create"
            )
        except Exception:
            raise

        return True

    def track_account_update(self, account):
        """
        Track Account update
        """
        try:
            self.inspetor_resource.track_account_action(
                account,
                "account_update"
            )
        except Exception:
            raise

        return True

    def track_account_deletion(self, account):
        """
        Track Account deletion
        """
        try:
            self.inspetor_resource.track_account_action(
                account,
                "account_delete"
            )
        except Exception:
            raise

        return True

    def track_event_creation(self, event):
        """
        Track Event creation
        """
        try:
            self.inspetor_resource.track_event_action(
                event,
                "event_create"
            )
        except Exception:
            raise

        return True

    def track_event_update(self, event):
        """
        Track Event update
        """
        try:
            self.inspetor_resource.track_event_action(
                event,
                "event_update"
            )
        except Exception:
            raise

        return True

    def track_event_deletion(self, event):
        """
        Track Event deletion
        """
        try:
            self.inspetor_resource.track_event_action(
                event,
                "event_delete"
            )
        except Exception:
            raise

        return True

    def track_item_transfer_creation(self, item_transfer):
        """
        Track Item Transfer creation
        """
        try:
            self.inspetor_resource.track_item_transfer_action(
                item_transfer,
                "item_transfer_create"
            )
        except Exception:
            raise

        return True

    def track_item_transfer_update(self, item_transfer):
        """
        Track Item Transfer update status
        """
        try:
            self.inspetor_resource.track_item_transfer_action(
                item_transfer,
                "item_transfer_update_status"
            )
        except Exception:
            raise

        return True

    def track_login(self, auth):
        """
        Track Login
        """
        try:
            self.inspetor_resource.track_account_auth_action(
                auth,
                "account_login"
            )
        except Exception:
            raise

        return True

    def track_logout(self, auth):
        """
        Track Logout
        """
        try:
            self.inspetor_resource.track_account_auth_action(
                auth,
                "account_logout"
            )
        except Exception:
            raise

        return True

    def track_password_reset(self, pass_recovery):
        """
        Track Password Reset
        """
        try:
            self.inspetor_resource.track_password_recovery_action(
                pass_recovery,
                "password_reset"
            )
        except Exception:
            raise

        return True

    def track_password_recovery(self, pass_recovery):
        """
        Track Password Recovery
        """
        try:
            self.inspetor_resource.track_password_recovery_action(
                pass_recovery,
                "password_recovery"
            )
        except Exception:
            raise

        return True

    def get_inspetor_account(self):
        return InspetorAccount()

    def get_inspetor_address(self):
        return InspetorAddress()

    def get_inspetor_auth(self):
        return InspetorAuth()

    def get_inspetor_category(self):
        return InspetorCategory()

    def get_inspetor_credit_card(self):
        return InspetorCreditCard()

    def get_inspetor_event(self):
        return InspetorEvent()

    def get_inspetor_item(self):
        return InspetorItem()

    def get_inspetor_pass_recovery(self):
        return InspetorPassRecovery()

    def get_inspetor_payment(self):
        return InspetorPayment()

    def get_inspetor_sale(self):
        return InspetorSale()

    def get_inspetor_session(self):
        return InspetorSession()

    def get_inspetor_transfer(self):
        return InspetorTransfer()
