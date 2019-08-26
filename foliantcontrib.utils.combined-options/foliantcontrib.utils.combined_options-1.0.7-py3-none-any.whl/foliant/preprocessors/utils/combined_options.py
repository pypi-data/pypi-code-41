import yaml
from pathlib import Path, PosixPath


class ValidationError(Exception):
    '''Error for validations when validation is failed'''
    pass


class RequiredParamsMissingError(Exception):
    '''Error for required params checking when requirement is not satisfied'''
    pass


class Options:
    '''
    Helper class which imitates dictionary with options but has some
    handy methods like option validation and conversion.
    '''

    def __init__(self,
                 options: dict,
                 defaults: dict = {},
                 convertors: dict = {},
                 validators: dict = {},
                 required: list = []):
        '''
        options (dict)    — options dictionary,
        defaults (dict)   — dictionary with default values (needed only for
                            is_default to work),
        convertors (dict) — dictionary with key = option name, value = function
                            which will be applied to the value of this option
                            before storing in class.
        validators (dict) — dictionary with key = option name, value = function
                            which will be applied to the value of this option.
                            Function should check for validity and raise
                            ValidationError if the check fails.
        required (list)   - list of required params or list of tuples with
                            combinations of required params.
        '''
        self.defaults = defaults
        self._options = options
        self._validators = validators
        self._convertors = convertors
        self._required = required
        self.validate()
        self._convert()

    @property
    def options(self):
        '''Actual options dictionary'''
        return self._options

    def validate(self):
        '''
        Validate all options with supplied validators and check for required
        params.
        Raises ValidationError if any of validation checks fails.
        Raises RequiredParamsMissingError if required params are not supplied.
        '''
        def _check_required(combination) -> bool:
            for param in combination:
                if param not in self.options:
                    return False
            return True

        for key in self._validators:
            if key in self.options:
                try:
                    self._validators[key](self.options[key])
                except ValidationError as e:
                    raise ValidationError(f'Error in option "{key}": {e}')
        if self._required:
            if isinstance(self._required[0], str):
                if not _check_required(self._required):
                    raise RequiredParamsMissingError(
                        f'Not all required params are supplied: {self._required}')
            else:  # several combinations of required params are possible
                check_result = any(_check_required(comb) for comb in self._required)
                if not check_result:
                    required_combs = "\nor:\n".\
                        join(str(comb).strip('()[]') for comb in self._required)
                    raise RequiredParamsMissingError(
                        f'Not all required params are supplied. '
                        f'Required parameter combinations are:\n{required_combs}')

    def _convert(self):
        '''
        Convert all options with supplied convertors and replace values in
        options dictionary in place.
        '''
        if not self._convertors:
            return

        for key in self._convertors:
            if key in self.options:
                convertor = self._convertors[key]
                self.options[key] = convertor(self.options[key])

    def is_default(self, option):
        '''return True if option value is same as default'''
        if option in self.defaults:
            return self.options[option] == self.defaults[option]
        return False

    def __str__(self):
        return f'<{self.__class__.__name__}{self.options}>'

    def __getitem__(self, ind: str):
        return self.options[ind]

    def __setitem__(self, ind: str, val):
        self.options[ind] = val
        self.validate()

    def __contains__(self, ind: str):
        return ind in self.options

    def __iter__(self):
        return iter(self.options.keys())

    def get(self, key, default=None):
        return self.options.get(key, default)

    def keys(self):
        return self.options.keys()

    def items(self):
        return self.options.items()

    def values(self):
        return self.options.values()


class CombinedOptions(Options):
    '''
    Helper class which combines several Options objects into one. If options
    interlap the one to be returned is defined by 'priority'.
    Apart from that it is a normal Options object.
    '''

    def __init__(self,
                 options: dict,
                 priority: str = None,
                 defaults: dict = {},
                 convertors: dict = {},
                 validators: dict = {},
                 required: list = []):
        '''
        options (dict) — dictionary where key = priority,
                         value = option dictionary.
        priority (str) — initial priority (if not set = first key from
                         options dict).
        other parameters are same as in parent
        '''
        self._options_dict = options
        self._validators = validators
        self._convertors = convertors
        self._required = required
        self.defaults = defaults
        self.priority = priority or next(iter(options.keys()))

    @property
    def priority(self):
        '''returns current priority'''
        return self._priority

    @priority.setter
    def priority(self, val: str):
        '''sets new priority and updates active options dictionary'''
        if val not in self._options_dict:
            raise ValueError('Priority must be one of: '
                             f'{", ".join(self._options_dict.keys())}. '
                             f'Value received: {val}')
        self._priority = val
        self.set_options()

    def set_options(self):
        '''
        Sets new active options dict with options combined from all options
        dicts with priority according to self.priority.
        '''

        self._options = {}
        priority_dict = self._options_dict[self.priority]

        for key in self._options_dict:
            if key != self.priority:
                self._options.update(self._options_dict[key])
        self._options.update(priority_dict)

        self.validate()
        self._convert()


def validate_in(supported, msg=None):
    '''
    Simple validator factory. Resulting function checks if option value
    is contained in supported collection.

    `supported` may be any collection-like object with __contains__ method.
    Raises ValueError otherwise.

    msg is message given to the ValiadtionError.

    Returns a validator function.'''

    DEFAULT_MSG = 'Unsupported option value {val}. Should be one '\
                  'of: {supported}'

    def validate(val):
        if val not in supported:
            raise ValidationError(message.format(val=val, supported=', '.join(supported)))

    if not hasattr(supported, '__contains__'):
        raise ValueError('`supported` should be a collection')

    message = msg if msg else DEFAULT_MSG

    return validate


def val_type(supported: list or type):
    '''
    Validator factory for validating param type.

    `supported` may be a type to check or a list (tuple) of possible types.
    '''

    MSG = 'Unsupported option value {val}. Must be of type {supported}'

    def validate(val):
        for type_ in types:
            if isinstance(val, type_):
                return
        raise ValidationError(MSG.format(val=val, supported=', '.join(str(t) for t in types)))
    if isinstance(supported, type):
        types = [supported]
    elif hasattr(supported, '__contains__'):
        types = supported
    else:
        raise ValueError('`supported` should be a type or a collection of types')
    return validate


def validate_exists(val):
    '''Validator that checks if path specified in val exists'''
    MSG = 'Path {val} does not exist.'
    if val and not Path(str).exists():
        raise ValidationError(MSG.format(val=val))


def path_convertor(option: str or PosixPath):
    '''convert string to Path'''
    if type(option) is str:
        return Path(yaml.load(option, yaml.Loader))
    else:
        return option


def yaml_to_dict_convertor(option: str or dict):
    '''convert yaml string or dict to dict'''

    if type(option) is dict:
        return option
    elif type(option) is str:
        return yaml.load(option, yaml.Loader)


def boolean_convertor(option):
    '''
    convert option to bool if necessary.

    Accepts True\False, 'tRuE' \ 'falSE', 1\0, Y \ n, yes \ no
    "other str" = True
    '''
    str_dict = {
        '1': True,
        '0': False,
        'y': True,
        'n': False,
        'yes': True,
        'no': False,
        'true': True,
        'false': False
    }
    if type(option) == bool:
        return option
    elif type(option) == int:
        return bool(int)
    elif type(option) == str:
        return str_dict.get(option.lower().strip(), True)


def rel_path_convertor(parent_path: str or PosixPath):
    '''
    Convertor factory which makes option path relative to parent_path supplied
    durint the convertor initialization.
    '''

    def _convertor(option):
        if not option:
            return option
        else:
            return Path(parent_path) / option

    return _convertor
