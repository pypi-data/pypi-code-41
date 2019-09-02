class WestWalletAPIException(Exception):
    pass


class InsufficientFundsException(WestWalletAPIException):
    pass


class CurrencyNotFoundException(WestWalletAPIException):
    pass


class IPNotAllowedException(WestWalletAPIException):
    pass


class WrongCredentialsException(WestWalletAPIException):
    pass


class TransactionNotFoundException(WestWalletAPIException):
    pass


class AccountBlockedException(WestWalletAPIException):
    pass


class BadAddressException(WestWalletAPIException):
    pass


class BadDestTagException(WestWalletAPIException):
    pass


class MinWithdrawException(WestWalletAPIException):
    pass


class MaxWithdrawException(WestWalletAPIException):
    pass


exceptions = {
    "account_blocked": AccountBlockedException,
    "bad_address": BadAddressException,
    "bad_dest_tag": BadDestTagException,
    "insufficient_funds": InsufficientFundsException,
    "currency_not_exist": CurrencyNotFoundException,
    "max_withdraw_error": MaxWithdrawException,
    "min_withdraw_error": MinWithdrawException,
    "currency_not_found": CurrencyNotFoundException,
    "not_found": TransactionNotFoundException
}