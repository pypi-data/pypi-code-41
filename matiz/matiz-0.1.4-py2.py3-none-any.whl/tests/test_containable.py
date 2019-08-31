import dataclasses

import matiz as iz


@dataclasses.dataclass
class ThatDataObject(iz.Containable):
    pass


def test_basic():
    c = ThatDataObject()

    assert c == ThatDataObject()
