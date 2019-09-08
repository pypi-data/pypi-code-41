# -*- coding:utf-8 -*-

"""
Hello from Tools/Math/Statistics.py

Functions:
    Count
        Returns the maximum value of occurrences and the number of occurrences.
    FilterAbnormalNum
        An abnormal number in a filtered list (large or small).
    FilterMaxMinNum
        A maximum number and a minimum number in a filtered list.
    Demo
        This function is a demo of all functions and classes in this module.
"""


# functions
def Count(data, start=0):
    """
    Returns the maximum value of occurrences and
    the number of occurrences. If there are more
    than one, return value will be more than one.

    Parameters
    ----------
    data : list
        A list of occurrences that need to be calculated,
        including int and float.
    start : int
        A legal start index.

    Returns
    -------
    list
        It's a list like that: [(5, 5), (7, 5)].
        The first value of the tuple in the list is
        the number that appears the most, and the
        second value is the number of times it appears.
    """
    assert isinstance(data, list), "Count requires list."
    data = data[start:]
    appear = {}
    for i in data:
        if i in list(appear.keys()):
            appear[i] += 1
        else:
            appear[i] = 1
    result = []
    keys = list(appear.keys())
    appear_num = list(appear.values())
    max_appear_num = max(appear_num)
    while True:
        try:
            index = appear_num.index(max_appear_num)
            result.append((keys[index], max_appear_num))
            del appear_num[index]
            del keys[index]
        except ValueError:
            break
    return result


def FilterAbnormalNum(data):
    """
    An abnormal number in a filter list (large or small).

    Parameters
    ----------
    data : list of int or list of float
        Many integers and float numbers that had to be filtered.

    Returns
    -------
    list
        It's a filtered list.
    """
    assert isinstance(data, list),\
        "FilterAbnormalNum requires list object."
    backup_data = data
    num_list = sorted(data)
    for i in num_list:
        assert isinstance(i, (int, float)),\
            "FilterAbnormalNum requires list object "\
            "containing only int and float."
    assert not len(num_list) < 3,\
        "FilterAbnormalNum requires list object "\
        "which length is bigger than 2."

    biggest = sorted(num_list[-2:], reverse=True)
    smallest = sorted(num_list[0:2], reverse=True)
    diff1 = biggest[0] - biggest[1]
    diff2 = smallest[0] - smallest[1]
    assert diff1 != diff2, "Can't find abnormal number."
    if diff1 > diff2:
        backup_data.remove(biggest[0])
        return backup_data
    else:
        backup_data.remove(smallest[1])
        return backup_data


def FilterMaxMinNum(data):
    """
    A maximum number and a minimum number in the filter list.
    If there are multiple maximum and minimum numbers,
    the filter appears first in the list.

    Parameters
    ----------
    data : list of int or list of float
        Many integers and float numbers that had to be filtered.

    Returns
    -------
    list
        It's a filtered list.
    """
    assert isinstance(data, list),\
        "FilterMaxMinNum requires list object."
    backup_data = data
    num_list = sorted(data)
    for i in num_list:
        assert isinstance(i, (int, float)), \
                "FilterMaxMinNum requires list object "\
                "containing only int and float."
    assert not len(num_list) < 3,\
        "FilterMaxMinNum requires list object "\
        "which length is bigger than 2."

    biggest = num_list[-1]
    smallest = num_list[0]
    assert biggest != smallest,\
        "Can't find biggest and smallest numbers."
    backup_data.remove(biggest)
    backup_data.remove(smallest)
    return backup_data


def Demo():
    """This function is a demo of all functions and classes in this module."""
    print(Count([1, 2, 3, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 1, 1, 2, 2, 2]))
    print(Count([1, 2, 3, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 1, 1, 2, 2, 2], 6))
    print(FilterAbnormalNum([1, 2, 2, 45]))
    print(FilterMaxMinNum([2, 4, 4, 7]))


if __name__ == '__main__':
    Demo()
