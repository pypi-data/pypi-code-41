import openpyxl
import pathlib


def is_integer(string):
    integers = str(1234567890)
    if string in integers:
        return True
    else:
        return False


def get_first_integer_sequence(value):
    """Search through string, return first set of consecutive numbers as single integer

    :param value:
    :return: integer. `0` if no integer was found
    """

    first_integer_set_found = False
    integer_string = ''
    output = -1  # default
    try:
        for char in value:
            if is_integer(char):
                # print(char)
                first_integer_set_found = True
                integer_string += char
            elif first_integer_set_found:
                break
            else:
                pass
        if integer_string != '':
            output = int(integer_string)
    finally:
        return output


def convert_to_string_with_leading_zeroes(value, min_length=0) -> str:
    """
    `84, 3` --> `084`
    `321, 1` --> `321`
    `hello, 3` --> `hello`
    :param value:
    :param min_length:
    :return:
    """
    output = '0' * min_length  # default output
    try:
        input_value = str(value)
        length = len(input_value)
        # print(f'length = {length}')
        missing_length = min_length - length
        if missing_length > 0:
            leading_zeroes = '0' * missing_length
            # print(f'leading zeroes = {leading_zeroes}')
            output = leading_zeroes + input_value
        else:
            output = input_value
    finally:
        return output



