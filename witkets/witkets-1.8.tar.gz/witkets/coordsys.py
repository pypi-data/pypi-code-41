"""Coordinate conversion utility classes.

This module provides the classes :class:`CoordConverter` and 
:class:`CoordSys2D`. The former is used for a single axis, while the latter is
used for 2-dimension cartesian coordinates.

Upon construction, these classes receives arguments defining the axes bounds,
expressed in world coordinates, and whether the axes are inverted.

Then, one can use the methods to convert to and from Normalized Device 
Coordinates [0..1].

**Example:**

    >>> import witkets as wtk
    >>> coord_sys = CoordSys2D(10, 20, -30, -10, y_inverted=True)
    >>> x, y = 15, -10
    >>> xn, yn = coord_sys.to_ndc(x, y)
    >>> x2, y2 = coord_sys.from_ndc(xn, yn)
    >>> print('  Original Coords: %s' % ([x, y]))
      Original Coords: [15, -10]
    >>> print('Normalized Coords: [%.1f, %.1f]' % (xn, yn))
    Normalized Coords: [0.5, 0.0]
    >>> print('  Loopback Coords: %s' % ([x2, y2]))
      Loopback Coords: [15.0, -10.0]

"""

class CoordConverter:
    """Coordinate conversions to/from Normalized Device Coordinates."""
    
    def __init__(self, minval, maxval, inverted=False):
        """Construct a coordinate converted with the supplied bounds."""
        self._minval = minval
        self._maxval = maxval
        self._delta = maxval - minval
        self._inverted = bool(inverted)

    @property
    def minval(self):
        """Minimum value (read-only)."""
        return self._minval

    @property
    def maxval(self):
        """Maximum value (read-only)."""
        return self._maxval

    @property
    def inverted(self):
        """Whether axis direction is inverted (read-only)."""
        return self._inverted

    def to_ndc(self, a):
        """Convert coordinate to normalized device coordinate [0..1]"""
        an = (a - self._minval) / self._delta
        if self.inverted:
            an = 1 - an
        return an

    def from_ndc(self, an):
        """Get coordinate from normalized device coordinates [0..1]"""
        if self.inverted:
            an = 1 - an
        return an * self._delta + self._minval

    def in_range(self, a):
        """Check if value is within the bounds for this coordinate system."""
        return self._minval <= a <= self._maxval

    def __str__(self):
        return ('CoordConverter(min=%f,max=%f,inv=%s)' % 
                    (self._minval, self._maxval, self.inverted)
        )


class CoordSys2D:
    """Pair of coordinate converters for X and Y"""

    def __init__(self, x_min, x_max, y_min, y_max, 
        x_inverted=False, y_inverted=False):
        self.xconv = CoordConverter(x_min, x_max, x_inverted)
        self.yconv = CoordConverter(y_min, y_max, y_inverted)

    def to_ndc(self, x, y):
        """Convert a point to normalized device coordinates [0..1]"""
        return self.xconv.to_ndc(x), self.yconv.to_ndc(y)

    def from_ndc(self, xn, yn):
        """Get coordinates from normalized device coordinates [0..1]"""
        return self.xconv.from_ndc(xn), self.yconv.from_ndc(yn)

    def in_range(self, x, y):
        """Check if value is within the range."""
        return self.xconv.in_range(x) and self.yconv.in_range(y)

    def __str__(self):
        return ('CoordSys[X(min=%f,max=%f,inv=%s),Y(min=%f,max=%f,inv=%s)]' % 
                    (self.xconv.minval, self.xconv.maxval, self.xconv.inverted,
                     self.yconv.minval, self.yconv.maxval, self.yconv.inverted)
        )


if __name__ == '__main__':
    import doctest
    doctest.testmod()

