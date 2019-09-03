# -*- coding: UTF-8 -*-
#! python3

"""
    Sample module to manage CSV reporting
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import csv
import logging
from pathlib import Path

# #############################################################################
# ########## Globals ###############
# ##################################


# #############################################################################
# ########## Classes ###############
# ##################################


class CsvReporter(object):
    """Produce CSV report. Inherits from standard 'csv.DictWriter' lib.

    See:
      - https://docs.python.org/fr/3.6/library/csv.html#csv.DictWriter
      - https://pymotw.com/3/csv/
    """

    def __init__(
        self,
        csvpath: Path = Path("./report.csv"),
        headers: list = ["header1", "header2"],
        extrahead: str = "ignore",
    ):
        """
            Instanciate class, check parameters and add object attributes.

            :param pathlib.Path csvpath: Path to the output file to write into. Default: `./report.csv`.
            :param list headers: list of CSV headers names (CSv first line). Default: `["header1", "header2"]`.
            :param str extrahead: linked to the `extrasection` option passed to the writer.
                It's the mode to handle cases where data is transmitted without header matching.
                Can be one of : `raise` or `ignore`. Default: `ignore`.
        """
        # check parameters
        if not isinstance(csvpath, Path):
            raise TypeError(
                "CSV path must be a 'pathlib.Path' instance not {}".format(
                    type(csvpath)
                )
            )
        if not isinstance(headers, list):
            raise TypeError(
                "Headers names must be a list, not {}".format(type(headers))
            )
        if extrahead.lower() not in ("raise", "ignore"):
            raise ValueError(
                "extrahead ({}) must be 'raise' or 'ignore'".format(extrahead)
            )
        # attributes
        csv.register_dialect("semicolon", delimiter=";")  # create dialect
        self.dialect = "semicolon"
        self.extrahead = "ignore"
        self.headers = headers
        self.csvpath = csvpath

        # write headers
        self.write_headers()
        logging.debug("CsvReporter instanciated")

    def write_headers(self):
        """Write headers to the CSV."""
        with self.csvpath.open(mode="w", newline="") as csvout:
            writer = csv.DictWriter(
                csvout, dialect=self.dialect, fieldnames=self.headers
            )
            writer.writeheader()
        logging.debug("Headers written: {}".format(self.headers))

    def add_unique(self, in_data: dict):
        """Add a single row to the CSV from the input data dictionary
        
        :param dict in_data: Dictionary of data to be added.
            Expected structure: `{header: value}`
        """
        # check parameters
        if not isinstance(in_data, dict):
            raise TypeError
        # add line
        with self.csvpath.open(mode="a", newline="") as csvout:
            writer = csv.DictWriter(
                csvout,
                dialect=self.dialect,
                fieldnames=self.headers,
                extrasaction=self.extrahead,
            )
            writer.writerow(in_data)
        logging.debug("New row added to the csv: {}".format(self.csvpath.name))

    def add_multiple(self, in_data: list):
        """Add a set of rows to the CSV from the input list of data dictionaries.
        
        :param list in_data: list of dictionaries of data to be added.
            Expected structure: `[{header1: valueA}, {header2: valueB}]`
        """
        # check parameters
        if not isinstance(in_data, list):
            raise TypeError

        # add line
        with self.csvpath.open(mode="a", newline="") as csvout:
            writer = csv.DictWriter(
                csvout,
                dialect=self.dialect,
                fieldnames=self.headers,
                extrasaction=self.extrahead,
            )
            writer.writerows(in_data)
        logging.debug(
            "{} rows added to the csv: {}".format(len(in_data), self.csvpath.name)
        )


# #############################################################################
# ### Stand alone execution #######
# #################################
if __name__ == "__main__":
    """Test parameters for a stand-alone run."""
    # logging
    logging.basicConfig(
        format="%(asctime)s || %(levelname)s "
        "|| %(module)s || %(funcName)s || %(lineno)s "
        "|| %(message)s",
        level=logging.DEBUG,
    )
    logging.debug("Standalone execution")
    # usage
    csv_report = CsvReporter(
        csvpath=Path("./report.csv"), headers=["Nom", "Chemin", "Objets", "Format"]
    )
    d = {"Nom": "Data", "Objets": 25, "Format": "ISO19139"}
    csv_report.add_unique(d)

    l = [d, d, d]
    csv_report.add_multiple(l)
