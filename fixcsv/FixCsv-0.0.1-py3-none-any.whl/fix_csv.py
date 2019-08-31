"""Fix csv module"""
import argparse
from typing import List
from difflib import SequenceMatcher
import pandas as pd


class FixCSV:
    """ Class to help fixing csv columns with the closest valid input"""

    def __init__(
        self,
        delimiter: str = ",",
        auto_fix: bool = True,
        quiet: bool = False,
        csv_path: str = None,
    ):
        """initialize class"""
        self.possible_values = []
        self.delimiter = delimiter
        self.auto_fix = auto_fix
        self.quiet = quiet
        self.fixed_csv = None
        self.csv_path = csv_path

    def set_possible_values(self, possible_values: List[str]):
        """set all possible values that the column could be"""
        self.possible_values = possible_values

    def add_possible_value(self, possible_value: str):
        """add a possible value to list"""
        self.possible_values.append(possible_value)

    def get_possible_values(self) -> List[str]:
        """return all possible values"""
        return self.possible_values

    def fix_csv_column(self, column: int, csv_path: str = None) -> List[str]:
        """read in csv and fix column"""
        if csv_path:
            csv = pd.read_csv(csv_path, delimiter=self.delimiter, header=None)
        else:
            print(self.csv_path)
            csv = pd.read_csv(self.csv_path, delimiter=self.delimiter, header=None)

        fixed_column = [self.edit_string(val) for val in list(csv.iloc[:, column])]
        csv.iloc[:, column] = pd.Series(fixed_column)
        self.fixed_csv = csv
        return fixed_column

    def edit_string(self, string_to_validate: str) -> str:
        """get ratios and fix string"""
        if string_to_validate in self.possible_values:
            return string_to_validate
        ratios = self.get_ratios(string_to_validate)
        if self.auto_fix:
            fixed_val = self.autofix_string(ratios, string_to_validate)
        else:
            fixed_val = self.manual_fix_string(ratios, string_to_validate)
        return fixed_val

    def get_ratios(self, string_to_validate: str) -> List[float]:
        """for each possible valid value, return the distance from the input string"""
        return [
            SequenceMatcher(None, val, string_to_validate).ratio()
            for val in self.possible_values
        ]

    def manual_fix_string(self, ratios, string_to_validate: str):
        """manually fix the string with bash inputs"""
        # https://stackoverflow.com/questions/13070461/get-index-of-the-top-n-values-of-a-list-in-python
        print("\n")
        sorted_ratios = sorted(
            range(len(ratios)), key=lambda i: ratios[i], reverse=True
        )
        print(string_to_validate)
        for i in range(1, 4):
            print(
                "[{}]: {} - {}".format(
                    i,
                    self.possible_values[sorted_ratios[i - 1]],
                    ratios[sorted_ratios[i - 1]],
                )
            )
        print("[4]: manual input")
        print("[5]: do not modify \n")
        valid_input = False
        while not valid_input:
            val = input("Top 3 most similar values: select an option: ")
            try:
                selection = int(val)
                if 0 < selection < 6:
                    valid_input = True
                    if selection == 5:
                        selected_value = string_to_validate
                    elif selection == 4:
                        selected_value = input(
                            "Write the input you want to replace the string with: "
                        )
                    else:
                        selected_value = self.possible_values[
                            sorted_ratios[selection - 1]
                        ]
                    print("You have selected: ", selected_value)

                else:
                    print("You have entered a number that is not an option")
            except TypeError:
                print("You have entered an invalid response")

        return selected_value

    def autofix_string(self, ratios, string_to_validate):
        max_ind = [ind for ind, val in enumerate(ratios) if val == max(ratios)]
        if len(max_ind) > 1:
            print("Warning: more than one values with max value")
        fixed_val = self.possible_values[max_ind.pop()]
        if not self.quiet:
            print(string_to_validate, "->", fixed_val)
        return fixed_val

    def read_possible_values(self, possible_values: str):
        with open(possible_values, "r") as file:
            val = [line.strip() for line in file]
        self.set_possible_values(val)


def main():
    parser = argparse.ArgumentParser(
        "automatically fixes csv columns with acceptable values"
    )
    parser.add_argument("csv_path", nargs=1)
    parser.add_argument("column", nargs=1)
    parser.add_argument("--possible_values", nargs="*")
    parser.add_argument("--output", nargs="?")
    parser.add_argument("--no-auto-fix", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    fcsv = FixCSV(csv_path=args.csv_path[0])
    fcsv.set_possible_values(args.possible_values)
    fcsv.fix_csv_column(column=int(args.column[0]))
    if args.output is not None:
        fcsv.fixed_csv.to_csv(
            args.output, index=None, header=None
        )
    else:
        for _, row in fcsv.fixed_csv.iterrows():
            print(row)


if __name__ == "__main__":
    main()
