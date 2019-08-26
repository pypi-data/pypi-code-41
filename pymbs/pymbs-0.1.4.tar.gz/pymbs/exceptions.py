"""
PyMBS is a Python library for use in modeling Mortgage-Backed Securities.

Copyright (C) 2019  Brian Farrell

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact: brian.farrell@me.com
"""

no_deal = (
    "\nNo deal has been loaded yet. "
    "Please load a deal before loading a model."
)

no_model = (
    "\nNo model has been loaded yet. "
    "Please load a model before continuing."
)


def _no_config_msg(pymbs_config_path, help_url):
    no_config_msg = (
        f"No pymbs configuration file was found at "
        f"{pymbs_config_path}"
        f"\nA blank file has been located at that location."
        f"\n\nPlease see {help_url}"
        f"\nfor information on how to edit the file before proceeding.\n"
    )
    return no_config_msg


class PrepaymentBenchmarkError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, prepayment_benchmark, message):
        self.prepayment_benchmark = prepayment_benchmark
        self.message = message


class DateError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, date, message):
        self.date = date
        self.message = message


class PayRuleError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, pay_rule, error):
        self.pay_rule = pay_rule
        self.error = error
        if self.error == 'invalid':
            self.message = f"The pay rule {pay_rule} is not a valid pay rule."
        elif self.error == 'no_parse':
            self.message = (
                f"The pay rule | {pay_rule} | was not parsed successfully. "
                f"\n\t\tPlease check the syntax."
            )

    def __str__(self):
        return self.message
