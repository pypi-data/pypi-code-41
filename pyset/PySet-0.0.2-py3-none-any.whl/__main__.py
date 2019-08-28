#!/usr/bin/python3
import argparse
from .pyset import PySet


def add_csv_args(pyset, csv_path, column):
    """add csv with column mapped from cli arguments"""
    pyset.add_csv(csv_path, list(map(int, column.split(","))))


def main():
    """main function"""
    parser = argparse.ArgumentParser(description="performs set operations on csvs")
    parser.add_argument("csvs", nargs="+")
    parser.add_argument("--columns", nargs="*")
    parser.add_argument("--operation", nargs="?")
    parser.add_argument("--delimiter", nargs="?")
    parser.add_argument("--full", action="store_true")
    args= parser.parse_args()
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
    main()
