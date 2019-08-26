import glob
import os
import re

import pytest

from psed.psed import Psed


def test_valid_patterns():
    psed = Psed(find=["pattern1", "pattern2"])
    assert psed.find == [re.compile("pattern1"), re.compile("pattern2")]


def test_invalid_patterns():
    with pytest.raises(SystemExit) as excinfo:
        Psed(find=["pattern1", "(pattern2"])
    assert (
        str(excinfo.value) == "Some find patterns have no been compiled successfully."
    )
