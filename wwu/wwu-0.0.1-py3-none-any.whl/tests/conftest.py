import pytest
from wwu import Box


@pytest.fixture
def box(scope="class"):
    return Box(10, 10, 20)
