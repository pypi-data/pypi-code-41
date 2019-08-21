from dataclasses import dataclass

from recept.env import ToEnvMixin


def env_class(prefix=None):
    @dataclass
    class EnvClass(ToEnvMixin):
        env_prefix = prefix

        str_value: str = "string"
        bytes_value: str = b"bytes"
        true_value: bool = True
        false_value: bool = False
        int_value: int = 42
        float_value: float = 3.14

        @staticmethod
        def expected(prefix):
            return {
                f"{prefix}STR_VALUE": "string",
                f"{prefix}BYTES_VALUE": "bytes",
                f"{prefix}TRUE_VALUE": "true",
                f"{prefix}FALSE_VALUE": "false",
                f"{prefix}INT_VALUE": "42",
                f"{prefix}FLOAT_VALUE": "3.14",
            }

    return EnvClass()


def nested_env_class(prefix=None, nested_prefix=None):
    @dataclass
    class NestedEnvClass(ToEnvMixin):
        env_prefix = prefix

        some_value: str = "foo"
        env_class: ToEnvMixin = env_class(prefix=nested_prefix)

        @staticmethod
        def expected(self_prefix, nest_prefix):
            env = {f"{self_prefix}SOME_VALUE": "foo"}
            env.update(env_class().expected(prefix=nest_prefix))
            return env

    return NestedEnvClass()


def test_prefix():
    # None
    obj = env_class()
    assert obj.to_env() == obj.expected(prefix="ENV_CLASS_")

    # Empty
    obj = env_class(prefix="")
    assert obj.to_env() == obj.expected(prefix="")

    # Custom
    obj = env_class(prefix="foo-bar")
    assert obj.to_env() == obj.expected(prefix="FOO_BAR_")


def test_nested():
    # None, None
    obj = nested_env_class()
    assert obj.to_env() == obj.expected(
        self_prefix="NESTED_ENV_CLASS_", nest_prefix="ENV_CLASS_"
    )

    # None, Empty
    obj = nested_env_class(nested_prefix="")
    assert obj.to_env() == obj.expected(
        self_prefix="NESTED_ENV_CLASS_", nest_prefix=""
    )

    # None, Custom
    obj = nested_env_class(nested_prefix="foo bar")
    assert obj.to_env() == obj.expected(
        self_prefix="NESTED_ENV_CLASS_", nest_prefix="FOO_BAR_"
    )

    # Empty, None
    obj = nested_env_class(prefix="")
    assert obj.to_env() == obj.expected(
        self_prefix="", nest_prefix="ENV_CLASS_"
    )

    # Empty, Empty
    obj = nested_env_class(prefix="", nested_prefix="")
    assert obj.to_env() == obj.expected(self_prefix="", nest_prefix="")

    # Empty, Custom
    obj = nested_env_class(prefix="", nested_prefix="foo! bar")
    assert obj.to_env() == obj.expected(self_prefix="", nest_prefix="FOO_BAR_")

    # Custom, None
    obj = nested_env_class(prefix="foo-bar")
    assert obj.to_env() == obj.expected(
        self_prefix="FOO_BAR_", nest_prefix="ENV_CLASS_"
    )

    # Custom, Empty
    obj = nested_env_class(prefix="FIZZ  !  buzz", nested_prefix="")
    assert obj.to_env() == obj.expected(
        self_prefix="FIZZ_BUZZ_", nest_prefix=""
    )

    # Custom, Custom
    obj = nested_env_class(prefix="a", nested_prefix="b")
    assert obj.to_env() == obj.expected(self_prefix="A_", nest_prefix="B_")
