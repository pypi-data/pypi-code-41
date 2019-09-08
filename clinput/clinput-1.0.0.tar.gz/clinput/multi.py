def natural(message, err="Please only enter positive integers.",
            zero=False, sep=" "):
    """Command line input and error checking for natural numbers.
    Args:
        message (str): The input message displayed in the command line.
        err (str, optional): The message displayed for an erroneous input.
            Defaults to "Please only enter positive integers.".
        zero (bool, optional): Zero status. True includes zero, False excludes
            zero. Defaults to False.
        sep (str, optional): The character used to separate inputs. Defaults
            to " ".

    Returns:
        list of [int,]: The first sucessfully input list of natural numbers.
    """
    # check whether natural numbers includes zero (default excludes zero)
    if zero:
        minimum = 0
    else:
        minimum = 1

    # loop until valid input given
    while True:
        # user input
        data = input(message)

        # error if no input
        if data == "":
            print("Please provide an input.")
            continue

        # split input using the separation character (space by default)
        split = data.split(sep)

        # check each item in the list
        split = __check_natural(split, minimum)

        # message and loop if invalid inputs, otherwise return list
        if split is None:
            print(err)
            continue
        return split


def __check_natural(items, minimum):
    """Checks a list of strings whether items are valid natural numbers.

    Args:
        items (list of [str,]): The list of items to test.
        minimum (int): The minimum acceptable natural number (0 or 1).

    Returns:
        list of [int,]: The list of items converted to natural numbers. Returns
            None if any one test fails.
    """
    for i, item in enumerate(items):
        # if decimal point is present, cannot be integer
        if "." in item:
            print("Failed on item: \"{}\"".format(item))
            return None

        # if input cannot be converted to integer, cannot be integer
        try:
            items[i] = int(item)
        except ValueError:
            print("Failed on item: \"{}\"".format(item))
            return None

        # check if integer is natural number (using zero definition above)
        if items[i] < minimum:
            print("Failed on item: \"{}\"".format(item))
            return None

    # if all code has run, return a list of natural numbers
    return items


def integer(message, err="Please only enter integers.", sep=" "):
    """Command line input and error checking for integers.
    Args:
        message (str): The input message displayed in the command line.
        err (str, optional): The message displayed for an erroneous input.
            Defaults to "Please only enter integers.".
        sep (str, optional): The character used to separate inputs. Defaults
            to " ".

    Returns:
        list of [int,]: The first sucessfully input list of integers.
    """
    # loop until valid input given
    while True:
        # user input
        data = input(message)

        # error if no input
        if data == "":
            print("Please provide an input.")
            continue

        # split input using the separation character (space by default)
        split = data.split(sep)

        # check each item in the list
        split = __check_integer(split)

        # message and loop if invalid inputs, otherwise return list
        if split is None:
            print(err)
            continue
        return split


def __check_integer(items):
    """Checks a list of strings whether items are valid integers.

    Args:
        items (list of [str,]): The list of items to test.

    Returns:
        list of [int,]: The list of items converted to integers. Returns None
            if any one test fails.
    """
    for i, item in enumerate(items):
        # if decimal point is present, cannot be integer
        if "." in item:
            print("Failed on item: \"{}\"".format(item))
            return None

        # if input cannot be converted to integer, cannot be integer
        try:
            items[i] = int(item)
        except ValueError:
            print("Failed on item: \"{}\"".format(item))
            return None

    # if all code has run, return a list of integers
    return items


def number(message, err="Please only enter numbers.", sep=" "):
    """Command line input and error checking for numbers.
    Args:
        message (str): The input message displayed in the command line.
        err (str, optional): The message displayed for an erroneous input.
            Defaults to "Please only enter numbers.".
        sep (str, optional): The character used to separate inputs. Defaults
            to " ".

    Returns:
        list of [float,]: The first sucessfully input list of numbers.
    """
    # loop until valid input given
    while True:
        # user input
        data = input(message)

        # error if no input
        if data == "":
            print("Please provide an input.")
            continue

        # split input using the separation character (space by default)
        split = data.split(sep)

        # check each item in the list
        split = __check_number(split)

        # message and loop if invalid inputs, otherwise return list
        if split is None:
            print(err)
            continue
        return split


def __check_number(items):
    """Checks a list of strings whether items are valid numbers.

    Args:
        items (list of [str,]): The list of items to test.

    Returns:
        list of [float,]: The list of items converted to floats. Returns None
            if any one test fails.
    """
    for i, item in enumerate(items):
        # if input cannot be converted to float, cannot be valid number
        try:
            items[i] = float(item)
        except ValueError:
            print("Failed on item: \"{}\"".format(item))
            return None

    # if all code has run, return a list of integers
    return items


def boolean(message, err="Please only enter 1s (True) or 0s (False).",
            sep=" "):
    """Command line input and error checking for boolean values (1 or 0).
    Args:
        message (str): The input message displayed in the command line.
        err (str, optional): The message displayed for an erroneous input.
            Defaults to "Please only enter 1s (True) or 0s (False).".
        sep (str, optional): The character used to separate inputs. Defaults
            to " ".

    Returns:
        list of [bool,]: The first sucessfully input list of boolean values.
    """
    # loop until valid input given
    while True:
        # user input
        data = input(message)

        # error if no input
        if data == "":
            print("Please provide an input.")
            continue

        # split input using the separation character (space by default)
        split = data.split(sep)

        # check each item in the list
        split = __check_boolean(split)

        # message and loop if invalid inputs, otherwise return list
        if split is None:
            print(err)
            continue
        return split


def __check_boolean(items):
    """Checks a list of strings whether items are valid boolean values (1 or 0).

    Args:
        items (list of [str,]): The list of items to test.

    Returns:
        list of [bool,]: The list of items converted to boolean values. Returns
        None ifany one test fails.
    """
    for i, item in enumerate(items):
        # if input cannot be converted to float, cannot be valid number
        if item == "1":
            items[i] = True
        elif item == "0":
            items[i] = False
        else:
            print("Failed on item: \"{}\"".format(item))
            return None

    # if all code has run, return a list of integers
    return items


def positive(message, err="Please only enter positive numbers.",
             zero=True, sep=" "):
    """Command line input and error checking for positive numbers.
    Args:
        message (str): The input message displayed in the command line.
        err (str, optional): The message displayed for an erroneous input.
            Defaults to "Please only enter positive numbers.".
        zero (bool, optional): Zero status. True includes zero, False excludes
            zero. Defaults to True.
        sep (str, optional): The character used to separate inputs. Defaults
            to " ".

    Returns:
        list of [float,]: The first sucessfully input list of positive numbers.
    """
    # loop until valid input given
    while True:
        # user input
        data = input(message)

        # error if no input
        if data == "":
            print("Please provide an input.")
            continue

        # split input using the separation character (space by default)
        split = data.split(sep)

        # check each item in the list
        split = __check_positive(split, zero)

        # message and loop if invalid inputs, otherwise return list
        if split is None:
            print(err)
            continue
        return split


def __check_positive(items, zero):
    """Checks a list of strings whether items are valid positive numbers.

    Args:
        items (list of [str,]): The list of items to test.
        zero (bool): Zero status. True includes zero, False excludes zero.

    Returns:
        list of [float,]: The list of items converted to positive numbers.
            Returns None if any one test fails.
    """
    for i, item in enumerate(items):
        # if input cannot be converted to float, cannot be number
        try:
            items[i] = float(item)
        except ValueError:
            print("Failed on item: \"{}\"".format(item))
            return None

        # check if integer is postive number (using zero definition above)
        if zero:
            if items[i] < 0:
                print("Failed on item: \"{}\"".format(item))
                return None
        else:
            if items[i] <= 0:
                print("Failed on item: \"{}\"".format(item))
                return None

    # if all code has run, return a list of natural numbers
    return items


def negative(message, err="Please only enter negative numbers.",
             zero=True, sep=" "):
    """Command line input and error checking for negative numbers.
    Args:
        message (str): The input message displayed in the command line.
        err (str, optional): The message displayed for an erroneous input.
            Defaults to "Please only enter negative numbers.".
        zero (bool, optional): Zero status. True includes zero, False excludes
            zero. Defaults to True.
        sep (str, optional): The character used to separate inputs. Defaults
            to " ".

    Returns:
        list of [float,]: The first sucessfully input list of negative numbers.
    """
    # loop until valid input given
    while True:
        # user input
        data = input(message)

        # error if no input
        if data == "":
            print("Please provide an input.")
            continue

        # split input using the separation character (space by default)
        split = data.split(sep)

        # check each item in the list
        split = __check_negative(split, zero)

        # message and loop if invalid inputs, otherwise return list
        if split is None:
            print(err)
            continue
        return split


def __check_negative(items, zero):
    """Checks a list of strings whether items are valid negative numbers.

    Args:
        items (list of [str,]): The list of items to test.
        zero (bool): Zero status. True includes zero, False excludes zero.

    Returns:
        list of [float,]: The list of items converted to negative numbers.
            Returns None if any one test fails.
    """
    for i, item in enumerate(items):
        # if input cannot be converted to float, cannot be number
        try:
            items[i] = float(item)
        except ValueError:
            print("Failed on item: \"{}\"".format(item))
            return None

        # check if integer is negative number (using zero definition above)
        if zero:
            if items[i] > 0:
                print("Failed on item: \"{}\"".format(item))
                return None
        else:
            if items[i] >= 0:
                print("Failed on item: \"{}\"".format(item))
                return None

    # if all code has run, return a list of natural numbers
    return items


def custom(message, allowed, err="Invalid input.", sep=" "):
    """Command line input and error checking for user-defined allowable inputs.
    Args:
        message (str): The input message displayed in the command line.
        allowed (tuple of (str,)): The allowable user inputs.
        err (str, optional): The message displayed for an erroneous input.
            Defaults to "Invalid input.".
        sep (str, optional): The character used to separate inputs. Defaults
            to " ".

    Returns:
        list of [str,]: The first sucessfully input list of allowed strings.
    """
    # loop until valid input given
    while True:
        # user input
        data = input(message)

        # error if no input
        if data == "":
            print("Please provide an input.")
            continue

        # split input using the separation character (space by default)
        split = data.split(sep)

        # check each item in the list
        split = __check_custom(split, allowed)

        # message and loop if invalid inputs, otherwise return list
        if split is None:
            print(err)
            continue
        return split


def __check_custom(items, allowed):
    """Checks a list of strings whether items are allowed.

    Args:
        items (list of [str,]): The list of items to test.
        allowed (tuple of (str,)): The allowable user inputs.

    Returns:
        list of [str,]: The list of items. Returns None if any one test fails.
    """
    for i, item in enumerate(items):
        if item not in allowed:
            print("Failed on item: \"{}\"".format(item))
            return None

    # if all code has run, return a list of items
    return items
