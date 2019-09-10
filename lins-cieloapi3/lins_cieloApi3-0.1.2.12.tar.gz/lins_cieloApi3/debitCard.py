
from .objectJSON import ObjectJSON

class DebitCard(ObjectJSON):

    def __init__(self,security_code, brand):

        self.card_number = None
        self.security_code = security_code
        self.holder = None
        self.expiration_date = None
        self.brand = brand
        self.customer_name = None
