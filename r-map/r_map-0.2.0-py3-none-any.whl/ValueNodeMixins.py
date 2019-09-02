from .ValidationError import ValidationError
class UnsignedValueNodeMixin:
    """Mixin for nodes which are expected to have an unsigned value. Additional
    behavior is also provided for classes of this type"""

    @property
    def value(self):
        raise NotImplementedError

    def validate(self):
        yield from super().validate()
        val = self.value
        if val < 0:
            yield ValidationError(
                   self,
                   f'Value is expected to be >= 0. Got: {val}')
        if not self.name or self.name.isspace():
            yield ValidationError(self, 'Name is whitespace or empty')

