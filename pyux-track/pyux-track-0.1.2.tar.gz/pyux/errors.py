
class ColorValueError(ValueError):
    """Color is not available for ColourPen."""
    pass


class StyleValueError(ValueError):
    """Style is not available for ColourPen."""
    pass


class NoDurationsError(ValueError):
    """Durations were not yet computed in Chronos."""
    pass


class DelayTypeError(TypeError):
    """No delay was given to Timer."""
    pass
