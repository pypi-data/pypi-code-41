from src import csv_IO
from numpy import array
from numpy import array_equal


def test_csv_reader_h():
    data = array([[20, 50, 10, 20, 0], [30, 30, 30, 10, 0],
                  [10, 15, 20, 45, 10], [5, 5, 5, 0, 85],
                  [15, 0, 15, 10, 0], [20, 0, 20, 15, 5]])
    groups = array(["C", "C", "C", "H", "H", "H"])
    sampleHeaders = array(["", "A", "B", "C", "D", "E", ""], dtype=str)
    speciesHeaders = array(["1", "2", "3", "4", "5", "6"], dtype=str)
    inputMatrix = csv_IO.csv_reader("data/testcsv.csv", False)

    assert array_equal(data, inputMatrix.data)
    assert array_equal(groups, inputMatrix.groups)
    assert array_equal(speciesHeaders, inputMatrix.speciesHeaders)
    assert array_equal(sampleHeaders, inputMatrix.sampleHeaders)


def test_csv_reader_nh():
    data = array([[20, 50, 10, 20, 0], [30, 30, 30, 10, 0],
                  [10, 15, 20, 45, 10], [5, 5, 5, 0, 85],
                  [15, 0, 15, 10, 0], [20, 0, 20, 15, 5]])
    groups = array(["C", "C", "C", "H", "H", "H"])
    sampleHeaders = array(["", "", "", "", "", ""], dtype=str)
    speciesHeaders = array(["", "", "", "", "", ""], dtype=str)
    inputMatrix = csv_IO.csv_reader("data/testcsvNH.csv", True)

    assert array_equal(data, inputMatrix.data)
    assert array_equal(groups, inputMatrix.groups)
    assert array_equal(speciesHeaders, inputMatrix.speciesHeaders)
    assert array_equal(sampleHeaders, inputMatrix.sampleHeaders)
