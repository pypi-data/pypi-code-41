import pandas
from primalytics.preprocessing.manipulations import bin_variable


class DataReader:
    def __init__(self, default_values_path):
        self._process = None

        self._input_data = {}
        self._input_data_processed = {}
        self._suppress_calculation = False

        self._warnings = []
        self._errors = []

        # default values -------------------------------------------------------
        self._variables_set_to_default = []
        with open(default_values_path, 'r') as f:
            lines = [x.replace('\n', '').split(',') for x in f.readlines()[1:]]
            self._default_values = {k: v for (k, v) in lines}

        for variable, default_value in self._default_values.items():
            try:
                new_default_value = float(default_value)
            except ValueError:
                pass
            else:
                if int(new_default_value) == new_default_value:
                    new_default_value = int(new_default_value)
                self._default_values.update({variable: new_default_value})

        self._error_messages = {
            KeyError:
                'missing key {key} in input_data dict. '
                'Setting default value.',
            ValueError:
                'wrong value \'{wrong_value}\' for variable \'{variable}\'. '
                'Setting default value.',
            TypeError:
                'wrong type \'{wrong_type}\' for variable '
                '\'{variable}\'. '
                'Setting default value.',
            ChoiceError:
                'value \'{wrong_value}\' not found in possible choices '
                'for variable \'{variable}\'. Setting default value.',
            AttributeError:
                'error for variable \'{variable}\'. Setting default value.'
        }

    def _get_error_message(self, error_type, **kwargs):

        message = self._error_messages[error_type].format(**kwargs)
        additional_message = kwargs.get('additional_message', '')

        package = {
            'type': error_type,
            'process': self._process,
            'message': message + additional_message
        }

        return package

    def _process_str(self, value, exceptions_handler,
                     set_lowercase: bool = False, set_uppercase: bool = False,
                     force_type=None):
        is_error = False

        if set_lowercase:
            value = str(value).lower()
        if set_uppercase:
            value = str(value).upper()
        if force_type is not None:
            try:
                value = force_type(value)
            except ValueError:
                is_error = True
                exceptions_handler.append(
                    'ValueError ({}): impossible to force type '
                    '{} on {}.'.format(self._process, force_type, value)
                )
        return value, is_error

    def _get_value(
            self,
            variable: str,
            exceptions_handler: list,
            is_crucial: bool = False,
            get_error: bool = False,
            new_name=None,
            set_default=True
    ):
        name = variable if new_name is None else new_name
        is_error = False
        value = None

        try:
            value = self._input_data[variable]
        except KeyError as kE:
            is_error = True

            exceptions_handler.append(
                self._get_error_message(
                    error_type=KeyError,
                    key=kE
                )
            )

            if is_crucial:
                self._suppress_calculation = True
            else:
                if set_default:
                    value = self._set_default_value(name)

        if get_error:
            return value, is_error
        else:
            return value

    def _get_str(
            self,
            variable: str,
            exceptions_handler: list,
            new_name: str = None,
            set_lowercase: bool = False,
            set_uppercase: bool = False,
            is_crucial: bool = False
    ):
        name = variable if new_name is None else new_name
        value, is_error = self._get_value(
            variable=variable,
            exceptions_handler=exceptions_handler,
            is_crucial=is_crucial,
            get_error=True,
            new_name=new_name
        )

        if not is_error:
            try:
                value = str(value)
            except (ValueError, TypeError) as error:
                exceptions_handler.append(
                    self._get_error_message(
                        error_type=type(error),
                        wrong_value=value,
                        wrong_type=type(value),
                        variable=variable
                    )
                )

                if is_crucial:
                    value = None
                    self._suppress_calculation = True
                else:
                    value = self._set_default_value(name)
            else:
                if set_lowercase:
                    value = value.lower()
                if set_uppercase:
                    value = str(value).upper()

        return value

    def _set_str(
            self,
            variable: str,
            exceptions_handler: list,
            new_name: str = None,
            set_lowercase: bool = False,
            set_uppercase: bool = False,
            is_crucial: bool = False
    ):
        name = variable if new_name is None else new_name
        value = self._get_str(
            variable=variable,
            exceptions_handler=exceptions_handler,
            new_name=new_name,
            set_lowercase=set_lowercase,
            set_uppercase=set_uppercase,
            is_crucial=is_crucial
        )
        self._input_data_processed.update({name: value})

    def _get_categorical(
            self,
            variable: str,
            choices: list,
            exceptions_handler: list,
            force_type=None,
            new_name: str = None,
            set_lowercase: bool = False,
            set_uppercase: bool = False,
            is_crucial: bool = False
    ):
        name = variable if new_name is None else new_name
        value, is_error = self._get_value(
            variable=variable,
            exceptions_handler=exceptions_handler,
            is_crucial=is_crucial,
            get_error=True,
            new_name=new_name
        )

        if not is_error:
            value, is_error = self._process_str(
                value=value,
                exceptions_handler=exceptions_handler,
                set_lowercase=set_lowercase,
                set_uppercase=set_uppercase,
                force_type=force_type
            )

            if value not in choices:
                is_error = True
                exceptions_handler.append(
                    self._get_error_message(
                        error_type=ChoiceError,
                        variable=name,
                        wrong_value=value
                    )
                )

            if is_error:
                if is_crucial:
                    value = None
                    self._suppress_calculation = True
                else:
                    value = self._set_default_value(name)

        return value

    def _set_categorical(
            self,
            variable: str,
            choices: list,
            exceptions_handler: list,
            force_type=None,
            new_name: str = None,
            set_lowercase: bool = False,
            set_uppercase: bool = False,
            is_crucial: bool = False
    ):
        name = variable if new_name is None else new_name
        value = self._get_categorical(
            variable=variable,
            choices=choices,
            exceptions_handler=exceptions_handler,
            force_type=force_type,
            new_name=new_name,
            set_lowercase=set_lowercase,
            set_uppercase=set_uppercase,
            is_crucial=is_crucial
        )
        self._input_data_processed.update({name: value})

    def _get_numeric(
            self,
            variable: str,
            exceptions_handler: list,
            numeric_type: type = int,
            new_name: str = None,
            is_crucial=False
    ):
        name = variable if new_name is None else new_name
        value, is_error = self._get_value(
            variable=variable,
            exceptions_handler=exceptions_handler,
            is_crucial=is_crucial,
            get_error=True,
            new_name=new_name
        )

        if not is_error:
            try:
                value = numeric_type(value)
            except (ValueError, TypeError) as error:
                exceptions_handler.append(
                    self._get_error_message(
                        error_type=type(error),
                        wrong_value=value,
                        wrong_type=type(value),
                        variable=variable
                    )
                )

                if is_crucial:
                    value = None
                    self._suppress_calculation = True
                else:
                    value = self._set_default_value(name)

        return value

    def _set_numeric(
            self,
            variable: str,
            exceptions_handler: list,
            numeric_type: type = int,
            min_value: int = None,
            max_value: int = None,
            width=None,
            binning_func=None,
            bucket: int = None,
            new_name: str = None,
            is_crucial=False
    ):
        name = variable if new_name is None else new_name
        value = self._get_numeric(
            variable=variable,
            exceptions_handler=exceptions_handler,
            numeric_type=numeric_type,
            new_name=new_name,
            is_crucial=is_crucial
        )

        if value != bucket:
            if width is not None and binning_func is not None:
                value = bin_variable(
                    s=value,
                    min_value=min_value,
                    max_value=max_value,
                    width=width,
                    how=binning_func
                )
            else:
                if min_value is not None:
                    value = max(min_value, value)
                if max_value is not None:
                    value = min(max_value, value)

        self._input_data_processed.update({name: value})

    def _get_date(
            self,
            variable: str,
            exceptions_handler: list,
            new_name: str = None,
            is_crucial: bool = False,
            timezone: str = 'Europe/London'
    ):
        name = variable if new_name is None else new_name
        date, is_error = self._get_value(
            variable=variable,
            exceptions_handler=exceptions_handler,
            is_crucial=is_crucial,
            get_error=True,
            new_name=new_name
        )

        if not is_error:
            try:
                date = pandas.to_datetime(date)
                if date is None:
                    raise ValueError
            except (ValueError, AttributeError) as error:
                self._warnings.append(
                    self._get_error_message(
                        error_type=type(error),
                        wrong_value=date,
                        variable=variable
                    )
                )

                if is_crucial:
                    date = None
                    self._suppress_calculation = True
                else:
                    date = self._set_default_value(name)
            else:
                try:
                    date = date.tz_convert(timezone)
                except TypeError:
                    date = date.tz_localize(timezone)

        return date

    def _set_date(
            self,
            variable: str,
            exceptions_handler: list,
            new_name: str = None,
            is_crucial=False,
            timezone: str = 'Europe/London'
    ):
        name = variable if new_name is None else new_name
        date = self._get_date(
            variable=variable,
            exceptions_handler=exceptions_handler,
            new_name=new_name,
            is_crucial=is_crucial,
            timezone=timezone
        )
        self._input_data_processed.update({name: date})

    def _set_default_value(self, variable):
        try:
            default_value = self._default_values[variable]
        except KeyError:
            raise KeyError(
                'Missing default value for variable {}'.format(variable)
            )
        else:
            self._variables_set_to_default.append(variable)

        return default_value

    def _reset(self):
        self._process = None

        self._input_data = {}
        self._input_data_processed = {}
        self._variables_set_to_default = []

        self._warnings = []
        self._errors = []

        self._suppress_calculation = False


class ChoiceError(Exception):
    pass
