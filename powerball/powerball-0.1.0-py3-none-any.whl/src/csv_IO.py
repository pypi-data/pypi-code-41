import numpy as np
import sys

from .dataMatrix import InputMatrix


def csv_reader(filename, noHeaderFlag):
    # Reads csv data to numpy arrays and outputs a InputMatrix containing them.
    # filename is the name of the file that will be read from i.e 'input.csv'
    # noHeaderFlag specifies that the input file doesn't have headers if true.

    try:
        with open(filename) as csvfile:
            # I would love to implement a lazy loading iterator approach here
            # to avoid effectively duplicating the input array during splicing,
            # but not sure on implementation. Maybe for later.
            inputArray = np.genfromtxt(csvfile, delimiter=',', dtype=str)

            if not noHeaderFlag:  # If headers exist
                sampleHeaders = np.reshape(inputArray[:1], inputArray.shape[1])
                speciesHeaders = inputArray[1:, 0]
                groups = inputArray[1:, -1]
                data = inputArray[1:, 1:-1].astype(int)
            else:
                speciesHeaders = np.full(inputArray.shape[1], "")
                sampleHeaders = np.full(inputArray.shape[0], "")
                groups = inputArray[0:, -1]
                data = inputArray[0:, 0:-1].astype(int)

            return InputMatrix(data, groups, sampleHeaders, speciesHeaders)

    except FileNotFoundError:
        print("File not found at", filename, file=sys.stderr)
        sys.exit()


def csv_writer(filename, outputArray):
    # Outputs data to a csv file.
    # filename is the name of the file that will be written to.
    # outputArray is the array that will be written to file composed of
    # a transposed array of unique group names, competitiveness scores,
    # comp p-values, lottery scores, and lottery p-values.

    try:
        np.savetxt(filename, outputArray,
                   delimiter=",", fmt="%s,%.15s,%.15s,%.15s,%.15s",
                   header=("Group,Comp Score,Comp Pval,"
                           "Lot Score,Lot Pval"),
                   comments="")
    except PermissionError:
        print("File output failed. Permissions not granted for", filename,
              file=sys.stderr)
    except:
        print("File output failed. Unknown Error.", file=sys.stderr)
