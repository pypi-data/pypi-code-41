import os
import json
import pytest
from pathlib import Path
from recept.env import Env, parse_value
from recept.errors import ImproperlyConfigured


OLD_ENVIRON = None


class TestData:
    url = "http://www.google.com/"
    json = dict(one="bar", two=2, three=33.44)
    dict = dict(foo="bar", test="on")
    path = "/home/dev"
    exported = "exported var"


def generate_data():
    return dict(
        STR_VAR="bar",
        MULTILINE_STR_VAR="foo\\nbar",
        INT_VAR="42",
        FLOAT_VAR="33.3",
        BOOL_TRUE_VAR="on",
        BOOL_TRUE_VAR2="True",
        BOOL_FALSE_VAR="0",
        BOOL_FALSE_VAR2="False",
        INT_LIST="42,33",
        INT_TUPLE="(42,33)",
        STR_LIST_WITH_SPACES=" foo,  bar",
        EMPTY_LIST="",
        DICT_VAR="foo=bar,test=on",
        URL_VAR=TestData.url,
        JSON_VAR=json.dumps(TestData.json),
        PATH_VAR=TestData.path,
        EXPORTED_VAR=TestData.exported,
    )


def assert_type_and_value(type_, expected, actual):
    assert isinstance(actual, type_)
    assert expected == expected


def setup_module(module):
    module.OLD_ENVIRON = os.environ
    os.environ = Env.ENVIRON = generate_data()


def teardown_module(module):
    os.environ = module.OLD_ENVIRON


@pytest.fixture
def env():
    return Env()


def test_not_present_with_default(env):
    assert 3 == env("not_present", default=3)


def test_not_present_without_default(env):
    with pytest.raises(ImproperlyConfigured):
        env("not_present")


def test_contains(env):
    assert "STR_VAR" in env
    assert "EMPTY_LIST" in env
    assert "I_AM_NOT_A_VAR" not in env


def test_str(env):
    assert_type_and_value(str, "bar", env("STR_VAR"))
    assert_type_and_value(str, "bar", env.str("STR_VAR"))
    assert_type_and_value(str, "foo\\nbar", env.str("MULTILINE_STR_VAR"))
    assert_type_and_value(
        str, "foo\nbar", env.str("MULTILINE_STR_VAR", multiline=True)
    )


def test_bytes(env):
    assert_type_and_value(bytes, b"bar", env.bytes("STR_VAR"))


def test_int(env):
    assert_type_and_value(int, 42, env("INT_VAR", cast=int))
    assert_type_and_value(int, 42, env.int("INT_VAR"))


def test_int_with_none_default(env):
    assert env("NOT_PRESENT_VAR", cast=int, default=None) is None


def test_float(env):
    assert_type_and_value(float, 33.3, env("FLOAT_VAR", cast=float))
    assert_type_and_value(float, 33.3, env.float("FLOAT_VAR"))


def test_bool_true(env):
    assert_type_and_value(bool, True, env("BOOL_TRUE_VAR", cast=bool))
    assert_type_and_value(bool, True, env("BOOL_TRUE_VAR2", cast=bool))
    assert_type_and_value(bool, True, env.bool("BOOL_TRUE_VAR"))


def test_bool_false(env):
    assert_type_and_value(bool, False, env("BOOL_FALSE_VAR", cast=bool))
    assert_type_and_value(bool, False, env("BOOL_FALSE_VAR2", cast=bool))
    assert_type_and_value(bool, False, env.bool("BOOL_FALSE_VAR"))


def test_int_list(env):
    assert_type_and_value(list, [42, 33], env("INT_LIST", cast=[int]))
    assert_type_and_value(list, [42, 33], env.list("INT_LIST", int))


def test_int_tuple(env):
    assert_type_and_value(tuple, (42, 33), env("INT_LIST", cast=(int,)))
    assert_type_and_value(tuple, (42, 33), env.tuple("INT_LIST", int))
    assert_type_and_value(tuple, ("42", "33"), env.tuple("INT_LIST"))


def test_str_list_with_spaces(env):
    assert_type_and_value(
        list, [" foo", "  bar"], env("STR_LIST_WITH_SPACES", cast=[str])
    )
    assert_type_and_value(
        list, [" foo", "  bar"], env.list("STR_LIST_WITH_SPACES")
    )


def test_empty_list(env):
    assert_type_and_value(list, [], env("EMPTY_LIST", cast=[int]))


def test_dict_value(env):
    assert_type_and_value(dict, TestData.dict, env.dict("DICT_VAR"))


def test_dict_parsing(env):
    assert parse_value("a=1", dict) == {"a": "1"}
    assert parse_value("a=1", dict(value=int)) == {"a": 1}
    assert parse_value("a=1,2,3", dict(value=[str])) == {"a": ["1", "2", "3"]}
    assert parse_value("a=1,2,3", dict(value=[int])) == {"a": [1, 2, 3]}
    assert parse_value(
        "a=1;b=1.1,2.2;c=3", dict(value=int, cast=dict(b=[float]))
    ) == {"a": 1, "b": [1.1, 2.2], "c": 3}

    assert parse_value(
        "a=uname;c=http://www.google.com;b=True",
        dict(value=str, cast=dict(b=bool)),
    ) == {"a": "uname", "c": "http://www.google.com", "b": True}


def test_url_value(env):
    url = env.url("URL_VAR")
    assert url.__class__ == env.URL_CLASS
    assert url.geturl() == TestData.url
    assert env.url("OTHER_URL", default=None) is None


def test_json_value(env):
    assert env.json("JSON_VAR") == TestData.json


def test_path(env):
    path = env.path("PATH_VAR")
    assert_type_and_value(Path, Path(TestData.path), path)


def test_smart_cast(env):
    assert env.get_value("STR_VAR", default="string") == "bar"
    assert env.get_value("BOOL_TRUE_VAR", default=True)
    assert not env.get_value("BOOL_FALSE_VAR", default=True)
    assert env.get_value("INT_VAR", default=1) == 42
    assert env.get_value("FLOAT_VAR", default=1.2) == 33.3


def test_exported(env):
    assert env("EXPORTED_VAR") == TestData.exported


def test_singleton_environ():
    config = generate_data()

    class MyEnv(Env):
        ENVIRON = config

    env = MyEnv()
    assert env.ENVIRON is config


def test_schema():
    env = Env(
        INT_VAR=int,
        NOT_PRESENT_VAR=(float, 33.3),
        STR_VAR=str,
        INT_LIST=[int],
        DEFAULT_LIST=([int], [2]),
    )

    assert_type_and_value(int, 42, env("INT_VAR"))
    assert_type_and_value(float, 33.3, env("NOT_PRESENT_VAR"))

    assert env("STR_VAR") == "bar"
    assert env("NOT_PRESENT2", default="foo") == "foo"

    assert_type_and_value(list, [42, 33], env("INT_LIST"))
    assert_type_and_value(list, [2], env("DEFAULT_LIST"))

    # Override schema in this one case
    assert_type_and_value(str, "42", env("INT_VAR", cast=str))
