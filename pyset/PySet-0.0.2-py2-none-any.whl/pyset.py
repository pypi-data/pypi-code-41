#!/usr/bin/python3
""" Pyset Module"""
import csv
import argparse


class PySet:
    """Performs set operations on csvs """

    def __init__(self):
        """initialize PySet class"""
        self.delimiter = ","
        self.columns = {}
        self.csv_paths = []
        self.csvs = []
        # Todo: set primary
        self.primary = 0
        self.full_output = False

    def set_full_output(self, full_output):
        self.full_output = full_output

    def add_csv(self, path_to_csv, columns=None):
        """add csv to class"""
        self.csv_paths.append(path_to_csv)
        self.columns[path_to_csv] = columns

    def read_csv(self, path_to_csv):
        """read in csv and subset columns"""
        try:
            cols = self.columns[path_to_csv]
        except KeyError:
            cols = None
        with open(path_to_csv) as csv_file:
            reader = csv.reader(csv_file, delimiter=self.delimiter)
            csvset = {}
            for ind, row in enumerate(reader):
                if cols:
                    csvset[ind] = tuple(row[column - 1] for column in cols)
                else:
                    csvset[ind] = tuple(row)

        return csvset

    def intersection(self):
        """
        make intersection of 2 csvsets
        """
        self.csvs = self.read_csv_list()
        csv0 = self.csvs[0]
        for csv1 in self.csvs[1:]:
            csv0 = self._intersection(csv0, csv1)
        return self._make_result(self._dedupe(csv0), self.full_output)

    def union(self):
        """ create union of 2 csvsets"""
        self.csvs = self.read_csv_list()
        union = {}
        ind = 0
        for csvset in self.csvs:
            for row in csvset.values():
                union[ind] = row
                ind += 1
        return self._make_result(self._dedupe(union), self.full_output)

    def complement(self):
        """compute the complement(not in) of 2 csvs"""
        self.csvs = self.read_csv_list()
        csv0 = self.csvs[0]
        for csv1 in self.csvs[1:]:
            csv0 = self._complement(csv0, csv1)
        return self._make_result(csv0, self.full_output)

    def dedupe(self):
        """dedupe csvset"""
        return self._make_result(self._dedupe(self.read_csv_list()[0]))

    def read_csv_list(self):
        """read in all csvs to csvset"""
        return [self.read_csv(csv_path) for csv_path in self.csv_paths]

    @staticmethod
    def _complement(csv0, csv1):
        """compute complement of 2 csvs"""
        return {key: row for key, row in csv0.items() if row not in csv1.values()}

    @staticmethod
    def _intersection(csv0, csv1):
        """compute intersection of 2 csvs"""
        return {ind: row for ind, row in csv0.items() if row in csv1.values()}

    @staticmethod
    def _dedupe(csvset, return_dupes=False):
        """dedupe but keep order
        https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-whilst-preserving-order"""
        seen = set()
        seen_add = seen.add
        deduped = {
            ind: row
            for ind, row in csvset.items()
            if not (row in seen or seen_add(row))
        }
        if return_dupes:
            return seen
        return deduped

    def _make_result(self, result, full_output=False):
        if full_output:
            with open(self.csv_paths[self.primary]) as csv_file:
                reader = csv.reader(csv_file, delimiter=self.delimiter)
                csvset = {}
                for ind, row in enumerate(reader):
                    if ind in result.keys():
                        csvset[ind] = tuple(row)
            return [val for val in csvset.values()]
        else:
            return [val for val in result.values()]


def add_csv_args(pyset, csv_path, column):
    """add csv with column mapped from cli arguments"""
    pyset.add_csv(csv_path, list(map(int, column.split(","))))


def main(args):
    """main function"""
    pyset = PySet()
    if args.delimiter:
        pyset.delimiter = args.delimiter

    if args.full:
        pyset.full_output = True

    if args.columns:
        if len(args.columns) == 1:
            for csv_path in args.csvs:
                add_csv_args(pyset, csv_path, args.columns[0])
        elif len(args.columns) == len(args.csvs):
            for csv_path, column in zip(args.csvs, args.columns):
                add_csv_args(pyset, csv_path, column)
        else:
            print("Not enough columns")
    else:
        for csv_path in args.csvs:
            pyset.add_csv(csv_path)

    if args.operation == "union":
        result = pyset.union()
    elif args.operation == "complement":
        result = pyset.complement()
    elif args.operation == "dedupe":
        if len(args.csvs) > 1:
            print("more than one csv, use union instead")
            result = []
        else:
            result = pyset.dedupe()
    elif args.operation is None or args.operation == "intersection":
        result = pyset.intersection()
    else:
        result = []
    for row in result:
        print(*row, sep=",")


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description="performs set operations on csvs")
    PARSER.add_argument("csvs", nargs="+")
    PARSER.add_argument("--columns", nargs="*")
    PARSER.add_argument("--operation", nargs="?")
    PARSER.add_argument("--delimiter", nargs="?")
    PARSER.add_argument("--full", action="store_true")
    ARGS = PARSER.parse_args()
    if ARGS.csvs:
        main(ARGS)
    else:
        print(ARGS)
