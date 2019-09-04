import six
from swimbundle_utils.exceptions import SwimlaneIntegrationException

if six.PY2:
    from validators import ValidationFailure as VfPy2
    
    class ValidationFailure(Exception):
        def __init__(self, func, args):
            self.vf = VfPy2(func, args)
            self.args = args
            self.func = func
            
        def __repr__(self):
            return "ValidationFailure - {}".format(self.vf.func.__name__)

else:
    from validators import ValidationFailure
    from validators import ValidationFailure as VfPy2

from pendulum.exceptions import ParserError
import validators
import pendulum


def asset_parser(context_asset, host_name="host",
                 username="username", password="password", auth=None):

    """
    Take in a context asset and break it into params for an __init__ call on BasicRestEndpoint
    :param context_asset: Context asset object
    :param host_name: host key name to grab from asset, defaults to 'host'
    :param username: username key name to grab from asset, defaults to 'username'
    :param password: password key name to grab from asset, defaults to 'password'
    :param auth: optional auth argument to override username/password. Set to None to disable auth
    :return: Dictionary of key args to use with **{} in the super().__init__() of a BasicRestEndpoint
    """
    
    params = {
        "host": context_asset[host_name],
        "verify": context_asset.get("verify_ssl", True),
        "proxy": context_asset.get("http_proxy")
    }

    if auth == "basic":  # nondefault auth
        params["auth"] = (context_asset[username], context_asset[password])
    elif auth:  # No auth, but not none (else is inferred to be no auth)
        params["auth"] = auth

    return params


def check_input(in_val, exp_val, flags=None, mapping=None, options=None):
    """
    Shorthand function for creating an InputChecker()
    :param in_val: Value to check 
    :param exp_val: Expected value(s)
    :param flags: Optional flags to pass to InputChecker
    :param mapping: Optional mapping to pass to InputChecker
    :param options: Optional options to pass to InputChecker
    :return: Parsed and Checked Value (if it passes, else raises SwimlaneIntegrationException)
    """
    return InputChecker(flags=flags, mapping=mapping, options=options).check(in_val, exp_val)


class InputChecker(object):
    MODE_APPEND = 0  # Parameter modes to override given params or append it to current params
    MODE_OVERRIDE = 1

    def __init__(self, flags=None, mapping=None, options=None):
        """
        Check the validity of a given set of inputs
        Apply Order:
        1. flags
        2. mappings
        3. options

        :param options: Special options to apply to given inputs, such as {"type": "int"}
        :param mapping: Change the inputs to another set, such as {True: "enable", False: "disable"}
        :param flags: Function to apply to input before any checking, like ["lower"]
        """
        
        self.options = options or {}  # {"type": "int"} etc
        self.mapping = mapping or {}  # {False: "disable"} etc
        self.flags = set(flags) if flags else set()  # ["lower"]
        
        # TODO link inputs? if a and b -> good else bad
        # TODO Wait until .validate() is called to check all inputs (possibility for linked inputs?)

        self.flag_funcs = {
            "lower": lambda x: x.lower(),
            "caps": lambda x: x.upper()
        }

        self.option_funcs = {
            "type": {
                "ipv4": self._validator_wrapper(validators.ipv4),
                "url": self._validator_wrapper(validators.url),
                "domain": self._validator_wrapper(validators.domain),
                "int": self._is_int,
                "datetime": self._is_datetime,
                "bool": self._is_boolean
            }
        }

    @staticmethod
    def _validator_wrapper(func):
        def validate_val(val):
            res = func(val)
            if res == True:
                return val
            if isinstance(res, ValidationFailure):
                raise res
            if isinstance(res, VfPy2):
                raise ValidationFailure(res.func, res.__dict__)

            raise Exception("Unknown validation error!")

        return validate_val

    def _is_boolean(self, value):
        if isinstance(value, bool):
            return True
        else:
            raise ValidationFailure(self._is_boolean, {"value": value})

    def _is_datetime(self, value):
        try:
            return pendulum.parse(value).to_iso8601_string()
        except ParserError:
            raise ValidationFailure(self._is_datetime, {"value": value})

    def _is_int(self, value):
        try:
            return int(value)
        except ValueError:
            raise ValidationFailure(self._is_int, {"value": value})

    def parse(self, val, flags=None, mapping=None, options=None):
        if not flags:
            flags = self.flags
        else:
            flags = self.flags.union(flags)

        if not options:
            options = self.options
        else:
            options.update(self.options)

        if not mapping:
            mapping = self.mapping
        else:
            mapping.update(self.mapping)
        # flags, mappings, options
        for flag in flags:
            if flag in self.flag_funcs:
                val = self.flag_funcs[flag](val)
            else:
                raise ValueError("Invalid flag '{}'".format(flag))

        if val in mapping:
            val = mapping[val]

        for option_k, option_v in six.iteritems(options):
            if option_k in self.option_funcs:
                if option_v in self.option_funcs[option_k]:
                    val = self.option_funcs[option_k][option_v](val)
                else:
                    raise ValueError("Invalid option value '{}'".format(option_v))
            else:
                raise ValueError("Invalid option '{}'".format(option_k))

        return val

    def check(self, val, expected=None, flags=None, mapping=None, options=None):
        try:
            val = self.parse(val, flags=flags, mapping=mapping, options=options)
        except ValidationFailure as e:
            raise SwimlaneIntegrationException("Invalid value '{val}' Exception: {e}".format(val=val, e=str(e)))

        if expected is not None:
            if val not in expected:
                raise SwimlaneIntegrationException("Unexpected value '{}', must be one of '{}'".format(val, expected))

        return val
