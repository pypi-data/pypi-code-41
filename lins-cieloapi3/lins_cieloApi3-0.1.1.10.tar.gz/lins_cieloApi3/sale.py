
from .objectJSON import ObjectJSON

class Sale(ObjectJSON):

    def __init__(self, merchant_order_id):

        self.merchant_order_id = merchant_order_id
        self.customer = None
        self.payment = None
        self.debitcard = None

    def update_return(self, r):

        payment = r.get('Payment') or {}
        debitcard = payment.get('DebitCard') or {}
        self.payment.payment_id = payment.get('PaymentId')
        self.payment.url = payment.get('Url')
        self.payment.authentication_url = payment.get('AuthenticationUrl') or {}
        self.payment.tid = payment.get('Tid')
        self.payment.status = payment.get('Status')
        self.payment.return_code = payment.get('ReturnCode')
        self.payment.proof_of_sale = payment.get('ProofOfSale')
        self.payment.debit_card.card_number = debitcard.get('CardNumber') or {}

        if self.payment.recurrent_payment:
            recurrent = payment.get('RecurrentPayment') or {}
            self.payment.recurrent_payment.recurrent_payment_id = recurrent.get('RecurrentPaymentId')
