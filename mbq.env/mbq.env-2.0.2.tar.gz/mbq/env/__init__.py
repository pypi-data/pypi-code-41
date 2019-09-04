import os
from enum import Enum


NOT_PROVIDED = object()


class EnvException(Exception):
    pass


class Environment(Enum):
    """
    A simple Enum to provide consistency in how we detect and
    represent the environment in which a service is running.
    """

    PRODUCTION = ('prd', 'Production')
    DEVELOPMENT = ('dev', 'Development')
    LOCAL = ('lcl', 'Local')
    TEST = ('lcl', 'Test')

    def __init__(self, short_name, long_name):
        self.short_name = short_name
        self.long_name = long_name
        self._searchable = {short_name.lower(), long_name.lower()}

    @property
    def is_deployed(self):
        return self in {self.PRODUCTION, self.DEVELOPMENT}

    @classmethod
    def _missing_(cls, value):
        """
        Extends the default value lookup behavior
        Environment(('prd', 'Production')) to accept either string (case-
        insensitive).

        >>> assert Environment.PRODUCTION is Environment('prd') is Environment('PRODUCTION')
        """
        for member in list(cls):
            if value.lower() in member._searchable:
                return member
        return super()._missing_(value)


class Env:
    def get(self, key, default=NOT_PROVIDED, required=True, coerce=NOT_PROVIDED):
        try:
            val = os.environ[key].strip()
        except KeyError as e:
            if default is not NOT_PROVIDED:
                return default

            if not required:
                return None

            raise EnvException('Missing key "{}"'.format(key)) from e

        if coerce is not NOT_PROVIDED:
            val = coerce(val)

        return val

    def get_environment(self, key, default=NOT_PROVIDED, required=True):
        return self.get(key, default=default, required=required, coerce=Environment)

    def get_int(self, key, default=NOT_PROVIDED, required=True):
        try:
            return self.get(key, default=default, required=required,
                            coerce=int)
        except ValueError as e:
            raise EnvException('Could not get int: {}'.format(e)) from e

    def get_bool(self, key, default=NOT_PROVIDED, required=True):
        def is_bool(val):
            if val == '1':
                return True
            elif val == '0':
                return False
            else:
                raise ValueError(f"{key} must be '1' or '0' (got '{val}')")

        return self.get(key, default=default, required=required, coerce=is_bool)

    def get_csv(self, key, default=NOT_PROVIDED, required=True):
        def splitter(val):
            return [s.strip() for s in val.split(',') if s.strip()]

        return self.get(key, default=default, required=required,
                        coerce=splitter)

    def get_tokens(self, key, default=NOT_PROVIDED, required=True):
        def splitter(val):
            return [s.strip() for s in val.split() if s.strip()]

        return self.get(key, default=default, required=required,
                        coerce=splitter)

    def get_key(self, guard_type, key, required=True):
        BEGIN_GUARD = '-----BEGIN {}-----'.format(guard_type)
        END_GUARD = '-----END {}-----'.format(guard_type)
        LINE_LENGTH = 64

        val = self.get(key, required=required)

        if not val:
            return val

        # ensure key begins and ends with guards
        if not val.startswith(BEGIN_GUARD) or not val.endswith(END_GUARD):
            raise EnvException('Key must have proper BEGIN and END guards')

        # if val already has newlines, we assume it's in the right format
        if '\n' in val:
            return val

        val = val[len(BEGIN_GUARD):-len(END_GUARD)]
        key_lines = [BEGIN_GUARD]

        while val:
            key_lines.append(val[:LINE_LENGTH])
            val = val[LINE_LENGTH:]

        key_lines.append(END_GUARD)

        return '\n'.join(key_lines)


_default = Env()  # no prefix for module-based use
get = _default.get
get_bool = _default.get_bool
get_csv = _default.get_csv
get_environment = _default.get_environment
get_int = _default.get_int
get_key = _default.get_key
get_tokens = _default.get_tokens
