

class EqOnAttrsMixin:
    """
    Allows class equality to be compared on the equality of the attribute names listed in equal_attrs.
    """
    equal_attrs = None

    def __eq__(self, other):
        if self.equal_attrs is None:
            return super().__eq__(other)

        for equal_attr in self.equal_attrs:
            if not hasattr(other, equal_attr): # other object doesn't have this property, must not be equal
                return False
            if getattr(self, equal_attr) != getattr(other, equal_attr):
                return False

        # passed all checks, must be equal
        return True


class EqOnAttrsWithConversionMixin(EqOnAttrsMixin):
    """
    Allows class equality to be compared on the equality of the attribute names listed in equal_attrs, converting
    all attributes to convert_type before comparing.
    """
    convert_type = str

    def __eq__(self, other):
        if self.equal_attrs is None:
            return self == other

        for equal_attr in self.equal_attrs:
            if not hasattr(other, equal_attr): # other object doesn't have this property, must not be equal
                return False
            if self.convert_type(getattr(self, equal_attr)) != self.convert_type(getattr(other, equal_attr)):
                return False

        # passed all checks, must be equal
        return True


class EqHashMixin:
    """
    Sets __hash__ based on attributes named in equal_attrs only.
    """
    equal_attrs = None

    def __hash__(self):
        return hash(tuple([getattr(self, attr) for attr in self.equal_attrs]))