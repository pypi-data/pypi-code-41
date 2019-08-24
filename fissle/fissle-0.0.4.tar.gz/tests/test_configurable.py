from unittest import TestCase
from fissle import c, NamedTuple


def test_schema_definition():
    @c
    class C(NamedTuple):
        a: int = 1  # desctiption


# def test_cli_definition():
#     """defining cli class with a method, but missing a doc string for method"""
#
#     @c
#     class Cli:
#         def x(self):
#             """docstring"""
#             pass


class TestConfigurable(TestCase):

    def setUp(self) -> None:
        @c
        class C(NamedTuple):
            a: int = 1  # desctiption

    def test_cli_definition(self):
        # """defining cli class with a method, but missing a doc string for method"""

        @c
        class Cli:
            def x(self):
                """docstring"""
                pass
