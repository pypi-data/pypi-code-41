import abc


class PaymentClient(object):
    def __init__(self, channel_name, timeout):
        self.channel_name = channel_name
        self.timeout = timeout

    @staticmethod
    def get_amount(amount):
        raise NotImplementedError

    @staticmethod
    def get_signature(params, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def init(self, payment, params):
        return {}

    @abc.abstractmethod
    def commit(self, payment, data):
        return {}

    @abc.abstractmethod
    def query(self, payment):
        return {}

    @abc.abstractmethod
    def inquiry(self, payment):
        return {}

    @abc.abstractmethod
    def cancel(self, payment):
        return {}

    @abc.abstractmethod
    def refund(self, payment, refund_payment):
        return {}
