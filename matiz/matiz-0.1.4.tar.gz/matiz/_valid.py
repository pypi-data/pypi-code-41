import dataclasses
import logging

from matiz._contain import is_represented_as_mapping
from . import _contain

_logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Violation:
    path_: str
    message: str

    def __str__(self):
        return f"{self.path_ or '<no path>'} | {self.message or '<no message given>'}"


class Validable:

    def is_valid(self):
        return not any(self.violations())

    def violations(self, path=None):
        if _contain.is_containable(self):
            path = path or self.__class__.__name__
            for i, (field_object, py_value) in enumerate(_contain.get_dataclass_items(self)):
                if is_represented_as_mapping(self):
                    sub_path = f"{path}.{field_object.name}"
                else:
                    sub_path = f"{path}[{i}]"

                yield from field_object.violations(py_value, sub_path)
        else:
            _logger.warning(
                f"Attempted to validate incompatible "
                f"object type: {self.__class__.__name__}.\n"
                f"It's supposed to be a dataclass.",
            )


@dataclasses.dataclass
class RangeValidator:
    minimum: int
    maximum: int

    def validate(self, value, path_):
        if self.minimum is not None and self.maximum is not None:
            assert self.minimum <= self.maximum, "Sick range definition. Min lower than max."

        if value is None:
            yield Violation(path_, f"Value cannot be None.")
            return
        if self.minimum is not None and value < self.minimum:
            yield Violation(path_, f"Value: {value!r} exceeds minimum: {self.minimum!r}.")
        if self.maximum is not None and value > self.maximum:
            yield Violation(path_, f"Value: {value!r} exceeds maximum: {self.maximum!r}.")
