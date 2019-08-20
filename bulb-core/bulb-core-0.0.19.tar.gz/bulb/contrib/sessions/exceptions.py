from bulb.db.exceptions import BULBNodeError

class BULBSessionError(Exception):
    pass


class BULBSessionDoesNotExist(BULBNodeError):
    pass


class BULBSessionDoesNotHaveData(BULBNodeError):
    pass
