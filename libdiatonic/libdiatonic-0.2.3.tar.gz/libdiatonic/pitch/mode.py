__all__ = ('Mode',)


class Mode(object):
    """ Class representing a specific mode which can be rooted at any note

    >>> major = Mode.Major
    >>> major
    Mode(Major)
    >>> ionian = Mode.Ionian
    >>> ionian == major
    True
    >>> ionian != major
    False
    >>> minor = Mode.Minor
    >>> ionian == minor
    False
    >>> ionian != minor
    True
    """

    # this will get filled in below
    _all_known_modes = []

    def _check_iterable_param(self, name, value):
        if type(value) not in (tuple, list):
            raise TypeError('{} must be an iterable, not {}'.format(name, type(value)))
        if not value:
            raise ValueError('cannot instantiate a Mode with empty {}'.format(name))

    def __init__(self, half_steps_pattern, names, shorthand=None, ionian_interval=None):
        self._check_iterable_param('half_steps_pattern', half_steps_pattern)
        self._check_iterable_param('names', names)
        self.half_steps_pattern = half_steps_pattern
        self.names = names
        self.shorthand = shorthand or []
        self.ionian_interval = ionian_interval

    @property
    def name(self):
        return self.names[0]

    @classmethod
    def all(cls):
        return cls._all_known_modes

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.name)

    def __eq__(self, other):
        if self.half_steps_pattern == other.half_steps_pattern:
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


known_modes = (
    ([2, 2, 1, 2, 2, 2, 1], ['Major', 'Ionian'], ['', 'M', 'maj'], 1),
    ([2, 1, 2, 2, 2, 1, 2], ['Dorian'], [], 2),
    ([1, 2, 2, 2, 1, 2, 2], ['Phrygian'], [], 3),
    ([2, 2, 2, 1, 2, 2, 1], ['Lydian'], [], 4),
    ([2, 2, 1, 2, 2, 1, 2], ['Mixolydian'], [], 5),
    ([2, 1, 2, 2, 1, 2, 2], ['Minor', 'Aeolian', 'Natural Minor'], ['-', 'm', 'min'], 6),
    ([1, 2, 2, 1, 2, 2, 2], ['Locrian'], [], 7)
)
for _pattern, _names, _shorthand, _interval in known_modes:
    for _name in _names:
        _property_name = _name.replace(' ', '_')
        setattr(Mode, _property_name, Mode(_pattern, _names, _shorthand, _interval))
        _mode_obj = getattr(Mode, _property_name)
        if not Mode._all_known_modes or _mode_obj != Mode._all_known_modes[-1]:
            Mode._all_known_modes.append(_mode_obj)
