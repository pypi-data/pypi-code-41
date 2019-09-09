from sesamutils import VariablesConfig

import pytest


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv('var1', 'value1')
    monkeypatch.setenv('var2', 'value2')
    monkeypatch.setenv('var4', 'value4')


def test_required_variables_is_set():
    required_vars = ["var1", "var2"]
    config = VariablesConfig(required_vars)

    assert config.var1 == "value1"
    assert config.var2 == "value2"


def test_optional_variable_with_default_value():

    required_vars = ["var1", "var2"]
    optional_vars = [("var3", "default_value")]
    config = VariablesConfig(required_vars, optional_vars)

    assert config.var3 == "default_value"


def test_optional_variable_without_default_value():

    required_vars = ["var1", "var2"]
    optional_vars = ["var4"]
    config = VariablesConfig(required_vars, optional_vars)

    assert config.var4 == "value4"


def test_validate_missing_variable():

    required_vars = ["var1", "var3"]
    config = VariablesConfig(required_vars)

    assert config.validate() == False
