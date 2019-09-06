import six
from six import string_types
from swimbundle_utils.exceptions import SwimlaneIntegrationException
from swimbundle_utils.validation import Validators, StopValidation
from validators import ValidationFailure
import base64


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


def create_attachment(filename, raw_data):
    """
    Easy way to create a single attachment. To create multiple attachments under a single key, use SwimlaneAttachment()
    :param filename: filname of the attachment
    :param raw_data: raw data of the file (pre-base64)
    :return: JSON data suitable for a key output in Swimlane
    """
    swa = SwimlaneAttachments()
    swa.add_attachment(filename, raw_data)
    return swa.get_attachments()


class SwimlaneAttachments(object):
    def __init__(self):
        self.attachments = []

    def add_attachment(self, filename, raw_data):
        if isinstance(raw_data, string_types) and not isinstance(raw_data, bytes):  # Needed for python3 support
            raw_data = raw_data.encode()
        
        self.attachments.append({
            "filename": filename,
            "base64": base64.b64encode(raw_data) 
        })
        
    def get_attachments(self):
        return self.attachments


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


def create_test_conn(base_cls, execute_func=None):
    """
    Create a test connection base class

    Ex:
    SwMain = create_test_conn(MyIntegration)
    Or:
    SwMain = create_test_conn(MyIntegration, "auth")

    :param base_cls: a Classtype of the ABCIntegration
    :param execute_func: the name of the function to call during execute, such as 'login'
    :return:
    """

    class SwMain(object):
        def __init__(self, context):
            self.context = context

        def execute(self):
            try:
                c = base_cls(self.context)
                if execute_func:
                    getattr(c, execute_func)()
                return {"successful": True}
            except Exception as e:
                return {"successful": False, "errorMessage": str(e)}
    return SwMain


class InputChecker(object):
    STOP_VALIDATION = StopValidation

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
        self.validators = Validators()

        # TODO link inputs? if a and b -> good else bad
        # TODO Wait until .validate() is called to check all inputs (possibility for linked inputs?)

        self.flag_funcs = {
            "lower": lambda x: x.lower(),
            "caps": lambda x: x.upper(),
            "optional": lambda x: InputChecker.STOP_VALIDATION if x is None else x
            # Stop validation on optional if it's None
        }

        self.option_funcs = {
            "type": self.validators.get_type_validators()
        }

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
        # Flags
        for flag in flags:
            if flag in self.flag_funcs:
                val = self.flag_funcs[flag](val)
            else:
                raise ValueError("Invalid flag '{}'".format(flag))

        # mappings
        if val in mapping:
            val = mapping[val]

        # options
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

        if val == InputChecker.STOP_VALIDATION:  # Parsed value says to stop validation, return None
            return None

        if expected is not None:  # If expected is None, the validation has been done in the .parse()
            if val not in expected:
                raise SwimlaneIntegrationException("Unexpected value '{}', must be one of '{}'".format(val, expected))

        return val
