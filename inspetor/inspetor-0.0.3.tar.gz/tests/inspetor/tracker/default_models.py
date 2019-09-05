from datetime import datetime

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


class DefaultModels(object):

    def get_default_sale(self):
        sale = InspetorSale()
        sale.id = "123"
        sale.account_id = "456"
        sale.total_value = "123,00"
        sale.status = "pending"
        sale.timestamp = datetime.timestamp(datetime.now())
        sale.items = [
            self.get_default_item()
        ]
        sale._payment = self.get_default_payment()

        return sale

    def get_default_update_sale(self):
        sale = InspetorSale()
        sale.id = "123"
        sale.timestamp = datetime.timestamp(datetime.now())
        sale.is_fraud = True
        sale.analyzed_by = "sift"

        return sale

    def get_default_account(self):
        account = InspetorAccount()
        account.id = "123"
        account.name = "Test"
        account.email = "test@email.com"
        account.document = "12312312312"
        account.phoneNumber = "112345678"
        account.address = self.get_default_address()
        account.timestamp = datetime.timestamp(datetime.now())

        return account

    def get_default_update_account(self):
        account = InspetorAccount()
        account.id = "123"
        account.timestamp = datetime.timestamp(datetime.now())

        return account

    def get_default_event(self):
        event = InspetorEvent()
        event.id = "123"
        event.name = "Name Test"
        event.description = "Description Test"
        event.sessions = [
            self.get_default_session()
        ]
        event.status = "private"
        event.slug = "slug-test"
        event.creator_id = "124"
        event.is_physical = True
        event.categories = [
            self.get_default_category()
        ]
        event.address = self.get_default_address()
        event.admins_id = ["123"]
        event.seating_options = ["Seating Option"]
        event.timestamp = datetime.timestamp(datetime.now())

        return event

    def get_default_update_event(self):
        event = InspetorEvent()
        event.id = "123"
        event.timestamp = datetime.timestamp(datetime.now())

        return event

    def get_default_transfer(self):
        transfer = InspetorTransfer()
        transfer.id = "123"
        transfer.timestamp = datetime.timestamp(datetime.now())
        transfer.item_id = "123"
        transfer.sender_account_id = "123"
        transfer.receiver_email = "test@email.com"
        transfer.status = "pending"

        return transfer

    def get_default_transfer_update(self):
        transfer = InspetorTransfer()
        transfer.id = "123"
        transfer.timestamp = datetime.timestamp(datetime.now())

        return transfer

    def get_default_auth(self):
        auth = InspetorAuth()
        auth.account_email = "test@email.com"
        auth.account_id = "123"
        auth.timestamp = datetime.timestamp(datetime.now())

        return auth

    def get_default_category(self):
        category = InspetorCategory()
        category.id = "123"
        category.name = "Category"

        return category

    def get_default_session(self):
        session = InspetorSession()
        session.id = "123"
        session.datetime = int(1562934682)

        return session

    def get_default_pass_recovery(self):
        pass_recovery = InspetorPassRecovery()
        pass_recovery.recovery_email = "test@email.com"
        pass_recovery.timestamp = datetime.timestamp(datetime.now())

        return pass_recovery

    def get_default_credit_card(self):
        credit_card = InspetorCreditCard()
        credit_card.first_six_digits = "123456"
        credit_card.last_four_digits = "1234"
        credit_card.holder_name = "Holder Name Test"
        credit_card.holder_cpf = "Holder CPF Test"
        credit_card.billing_address = self.get_default_address()

        return credit_card

    def get_default_address(self):
        address = InspetorAddress()
        address.street = "Test Stree"
        address.number = "123"
        address.zip_code = "123456"
        address.city = "Test City"
        address.state = "Test State"
        address.country = "Test Country"
        address.latitude = "123"
        address.longitude = "123"

        return address

    def get_default_item(self):
        item = InspetorItem()
        item.id = "123"
        item.event_id = "123"
        item.session_id = "123"
        item.seating_option = "Seating Option Test"
        item.price = "10"
        item.quantity = "123"

        return item

    def get_default_payment(self):
        payment = InspetorPayment()
        payment.id = "123"
        payment.method = "credit_card"
        payment.installments = "1"
        payment.credit_card = self.get_default_credit_card()

        return payment