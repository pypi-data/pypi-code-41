import unittest
from seperator.lines import line


class TestLinesFunctions(unittest.TestCase):
    def test_empty_call(self):
        self.assertEqual(
            line(), "\x1b[35m" + 80 * "─" + "\x1b[39m"
        )

    def test_info(self):
        self.assertEqual(
            line("INFORMATIVE TEXT"),
            "\x1b[35m"
            + "─"
            + " "
            + "INFORMATIVE TEXT"
            + " "
            + "─"
            * (80 - (2 + 1 + len("INFORMATIVE TEXT")))
            + "\x1b[39m",
        )

    def test_color(self):
        self.assertEqual(
            line(color="ReD"),
            "\x1b[31m" + 80 * "─" + "\x1b[39m",
        )

    def test_align(self):
        self.assertEqual(
            line("INFORMATIVE TEXT", align=-1),
            "\x1b[35m"
            + "─"
            * (80 - (2 + 1 + len("INFORMATIVE TEXT")))
            + " "
            + "INFORMATIVE TEXT"
            + " "
            + "─"
            + "\x1b[39m",
        )

    def test_margin(self):
        self.assertEqual(
            line("INFORMATIVE TEXT", margin=(2, 3)),
            "\x1b[35m"
            + "─"
            + " " * 2
            + "INFORMATIVE TEXT"
            + " " * 3
            + "─"
            * (80 - (5 + 1 + len("INFORMATIVE TEXT")))
            + "\x1b[39m",
        )

    def test_char(self):
        self.assertEqual(
            line(char="#"),
            "\x1b[35m" + 80 * "#" + "\x1b[39m",
        )


if __name__ == "__main__":
    unittest.main()
