import pandas as pd
import csv


def list_to_csv(lst, filename):
    df = pd.DataFrame(lst, columns=None)

    df.to_csv(filename, index=None, header=False)

# def list_to_csv(lst, filename):
#     df = pd.DataFrame(lst)
#     df.to_csv(filename)


# def list_from_csv(filename):
#     df = pd.read_csv(filename)
#     lst = list(df.iloc[:, 1])

#     return lst

def list_from_csv(filename):
    rows = []

    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)

        for row in csvreader:
            rows.append(row)

    return rows
