def natural(message, err="Please enter an integer greater than zero.",
            zero=False):
    """Command line input and error checking for natural numbers.

    Args:
        message (string): The input message displayed in the command line.
        err (string, optional): The message displayed for an erroneous input.
            Defaults to "Please enter an integer greater than zero.".
        zero (bool, optional): Zero status. True includes zero, False excludes
            zero. Defaults to False.

    Returns:
        int: The first sucessfully input natural number.
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

        # if blank, error
        if data.strip() == "":
            print("Please provide an input.")
            continue

        # if decimal point is present, cannot be integer
        if "." in data:
            print(err)
            continue

        # if input cannot be converted to integer, cannot be integer
        try:
            data = int(data)
        except ValueError:
            print(err)
            continue

        # check if integer is natural number (using zero definition above)
        if data < minimum:
            print(err)
            continue

        # if all code has run, natural number can be returned
        return data


def integer(message, err="Please enter an integer."):
    """Command line input and error checking for integers.

    Args:
        message (string): The input message displayed in the command line.
        err (string, optional): The message displayed for an erroneous input.
            Defaults to "Please enter an integer.".

    Returns:
        int: The first sucessfully input integer.
    """
    # loop until valid input given
    while True:
        # user input
        data = input(message)

        # if blank, error
        if data.strip() == "":
            print("Please provide an input.")
            continue

        # if decimal point is present, cannot be integer
        if "." in data:
            print(err)
            continue

        # if input cannot be converted to integer, cannot be integer
        try:
            data = int(data)
        except ValueError:
            print(err)
            continue

        # if all code has run, integer can be returned
        return data


def number(message, err="Please enter a number."):
    """Command line input and error checking for numbers.

    Args:
        message (string): The input message displayed in the command line.
        err (string, optional): The message displayed for an erroneous input.
            Defaults to "Please enter a number.".

    Returns:
        float: The first sucessfully input number.
    """
    # loop until valid input given
    while True:
        # user input
        data = input(message)

        # if blank, error
        if data.strip() == "":
            print("Please provide an input.")
            continue

        # if input cannot be converted to float, cannot be number
        try:
            data = float(data)
        except ValueError:
            print(err)
            continue

        # if all code has run, number can be returned
        return data


def string(message, err="Please provide an input."):
    """Command line input and error checking for strings (error if blank).

    Args:
        message (string): The input message displayed in the command line.
        err (string, optional): The message displayed for an erroneous input.
            Defaults to "Please provide an input.".

    Returns:
        string: The first sucessfully input string.
    """
    # loop until valid input given
    while True:
        # user input
        data = input(message)

        # if blank, error. otherwise, return input string
        if data.strip() == "":
            print(err)
            continue
        return data


def boolean(message, err="Please enter 1 (True) or 0 (False)."):
    """Command line input and error checking for boolean values (1 or 0).

    Args:
        message (string): The input message displayed in the command line.
        err (string, optional): The message displayed for an erroneous input.
            Defaults to "Please enter 1 (True) or 0 (False).".

    Returns:
        bool: The first sucessfully input boolean value.
    """
    # loop until valid input given
    while True:
        # user input
        data = input(message)

        # if blank, error
        if data.strip() == "":
            print("Please provide an input.")
            continue

        # if 1, return True. if 0, return false. else, error and loop
        if data == "1":
            return True
        elif data == "0":
            return False
        print(err)


def positive(message, err="Please enter a positive number.", zero=True):
    """Command line input and error checking for positive numbers.

    Args:
        message (string): The input message displayed in the command line.
        err (string, optional): The message displayed for an erroneous input.
            Defaults to "Please enter a positive number.".
        zero (bool, optional): Zero status. True includes zero, False excludes
            zero. Defaults to True.

    Returns:
        float: The first sucessfully input positive number.
    """
    # loop until valid input given
    while True:
        # user input
        data = input(message)

        # if blank, error
        if data.strip() == "":
            print("Please provide an input.")
            continue

        # if input cannot be converted to float, cannot be a valid number
        try:
            data = float(data)
        except ValueError:
            print(err)
            continue

        # check if integer is positive (setting zero bound using input
        # argument, default is to include zero)
        if zero:
            if data < 0:
                print(err)
                continue
        else:
            if data <= 0:
                print(err)
                continue

        # if all code has run, positive number can be returned
        return data


def negative(message, err="Please enter a negative number.", zero=True):
    """Command line input and error checking for negative numbers.

    Args:
        message (string): The input message displayed in the command line.
        err (string, optional): The message displayed for an erroneous input.
            Defaults to "Please enter a negative number.".
        zero (bool, optional): Zero status. True includes zero, False excludes
            zero. Defaults to True.

    Returns:
        float: The first sucessfully input negative number.
    """
    # loop until valid input given
    while True:
        # user input
        data = input(message)

        # if blank, error
        if data.strip() == "":
            print("Please provide an input.")
            continue

        # if input cannot be converted to float, cannot be a valid number
        try:
            data = float(data)
        except ValueError:
            print(err)
            continue

        # check if integer is negative (setting zero bound using input
        # argument, default is to include zero)
        if zero:
            if data > 0:
                print(err)
                continue
        else:
            if data >= 0:
                print(err)
                continue

        # if all code has run, negative number can be returned
        return data


def custom(message, allowed, err="Invalid input."):
    """Command line input and error checking for user-defined allowable inputs.

    Args:
        message (string): The input message displayed in the command line.
        allowed (tuple of (string,)): The allowable user inputs.
        err (string, optional): The message displayed for an erroneous input.
            Defaults to "Invalid input.".

    Returns:
        string: The first sucessfully allowed input string.
    """
    # loop until valid input
    while True:
        # user input
        data = input(message)

        # if blank, error
        if data.strip() == "":
            print("Please provide an input.")
            continue

        # check if input is in allowed range. if not, error and loop
        if data in allowed:
            return data
        print(err)
