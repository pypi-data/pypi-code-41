class Customer:
    def __init__(self, ip, country=None, email=None, locale=None):
        self.ip = ip
        self.country = country
        self.email = email
        self.locale = locale

    def validate(self):
        if self.ip is None:
            raise ValueError("IP is required")

    def dict(self):
        self.validate()
        return {k: v for k, v in
                {
                    "ip": self.ip,
                    "country": self.country,
                    "email": self.email,
                    "locale": self.locale,
                }.items()
                if v is not None
                }


class Transaction:
    def __init__(self, amount, currency, id=None, merchant_data=None,
                 recurring_required=None, reference=None,
                 cancel_url=None, notification_url=None, return_url=None):
        self.amount = amount
        self.currency = currency
        self.id = id
        self.merchant_data = merchant_data
        self.recurring_required = recurring_required
        self.reference = reference
        self.cancel_url = cancel_url
        self.notification_url = notification_url
        self.return_url = return_url

    def validate(self):
        if self.amount is None:
            raise ValueError("Amount is required")
        if self.currency is None:
            raise ValueError("Currency is required")
        callback_urls = [self.cancel_url, self.notification_url, self.return_url]
        callback_urls_noneness = [url is None for url in callback_urls]
        if sum(callback_urls_noneness) != 0 and sum(callback_urls_noneness) != 3:
            raise ValueError("Either no or all callback urls must be provided")

    def dict(self):
        self.validate()
        if self.cancel_url is not None and  self.notification_url is not None and self.return_url is not None:
            transaction_url = {
                "cancel_url": self.cancel_url,
                "notification_url": self.notification_url,
                "return_url": self.return_url,
                }
        return {k: v for k, v in
                {
                    "amount": self.amount,
                    "currency": self.currency,
                    "id": self.id,
                    "merchant_data": self.merchant_data,
                    "recurring_required": self.recurring_required,
                    "reference": self.reference,
                    "transaction_url": transaction_url,
                }.items()
                if v is not None
                }
