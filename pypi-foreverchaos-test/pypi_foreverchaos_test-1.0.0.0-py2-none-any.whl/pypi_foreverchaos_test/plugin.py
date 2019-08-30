import pytest


@pytest.yield_fixture(scope='class')
def get_double_data():
    yield 5 * 2


@pytest.yield_fixture(scope='class')
def generate_list(get_double_data):
    data = get_double_data
    new_list = [data]
    yield new_list
