class MissingValue(object): # pylint: disable=too-few-public-methods
  def __str__(self):
    return "MISSING"

class OptionalValue(object): # pylint: disable=too-few-public-methods
  def __str__(self):
    return "OPTIONAL"

MISSING_VALUE = MissingValue()
OPTIONAL_VALUE = OptionalValue()
