from src import statFunctions
from numpy import array


def test_two_tailed_upper():
    # Test the two tailed p-value function on the upper end on
    # a generated list from 1-100
    testList = array(range(1, 101))
    u = 60
    assert statFunctions.two_tailed_comparison(testList, u) == 0.4


def test_two_tailed_lower():
    # Test the two tailed p-value function on the lower end on
    # a generated list from 1-100
    testList = array(range(1, 101))
    u = 40
    assert statFunctions.two_tailed_comparison(testList, u) == 0.39


def test_two_tailed_zero():
    # Testing the two tailed comparison test on zero on
    # a generated list from 1-100
    testList = array(range(1, 101))
    u = 100
    assert statFunctions.two_tailed_comparison(testList, u) == 0.01


def test_two_tailed_mid():
    # Testing the two tailed comparison test on the middle value on
    # a generated list from 1-100
    testList = array(range(1, 101))
    u = 50
    assert statFunctions.two_tailed_comparison(testList, u) == 0.49


def test_one_tailed_low():
    # Testing the one tailed lower comparison tests on
    # a generated list from 1-100
    testList = array(range(1, 101))
    u = 40
    assert statFunctions.one_tailed_lower(testList, u) == 0.39
    assert statFunctions.one_tailed_upper(testList, u) == 0.6


def test_one_tailed_high():
    # Testing the two tailed comparison test on zero on
    # a generated list from 1-100
    testList = array(range(1, 101))
    u = 60
    assert statFunctions.one_tailed_lower(testList, u) == 0.59
    assert statFunctions.one_tailed_upper(testList, u) == 0.4


def test_one_tailed_zero():
    # Testing the two tailed comparison test on zero on
    # a generated list from 1-100
    testList = array(range(1, 101))
    u = 0
    assert statFunctions.one_tailed_lower(testList, u) == 0.01
    assert statFunctions.one_tailed_upper(testList, u) == 1


def test_one_tailed_mid():
    # Testing the two tailed comparison test on zero on
    # a generated list from 1-100
    testList = array(range(1, 101))
    u = 50
    assert statFunctions.one_tailed_lower(testList, u) == 0.49
    assert statFunctions.one_tailed_upper(testList, u) == 0.5
