from unittest import TestCase
from clima import c, Schema
from functools import partial


def test_schema_definition():
    @c
    class C(Schema):
        a: int = 1  # desctiption

def test_schema_without_doc():
    @c
    class C(Schema):
        a: int = 1

# TODO: sane exception for this scenario
# def test_schema_without_default():
#     @c
#     class C(Schema):
#         a: int

def test_schema_without_type():
    @c
    class C(Schema):
        a = 1


class TestConfigurable(TestCase):

    def setUp(self) -> None:
        @c
        class C(Schema):
            a: int = 1  # description

    def test_cli(self):
        """Basic Cli definition"""

        @partial(c, noprepare=True)
        class Cli:
            def x(self):
                """docstring"""
                pass

    def test_cli_without_ds(self):
        """Cli definition without a docstring"""

        @partial(c, noprepare=True)
        class Cli:
            def x(self):
                pass

