###########################################################################
#
# this module meant to provide general handling for string files
#
###########################################################################


# will turn string into a bool
def str2bool(v):
    if v is True:
        return True
    return v.lower() in ("yes", "true", "t", "1")


def str_to_words(string, incl_chars=None):
    """
    Will extract all of the words from a string to a list
    Args:
        :param string: the string to search upon
        :param incl_chars: if you want to include any more chars in the search, set them here. Like [',', ';', '[', '{'] -> no need to add escaping.
        :return: an array of the matching words
    """
    pattern = '\w+'
    if incl_chars is not None:
        incl_chars = add_escape_before_special(incl_chars)
        joined_chars = ''.join(incl_chars)
        pattern = '[' + joined_chars + '\w]+'

    import re
    return re.findall(pattern, string)


def add_escape_before_special(special_arr):
    """
    Will check if the array contains special chars. If it does, will add \ before each letter
    :param special_arr: an array which quite possibly contain special chars
    :return: an escaped array
    """
    for i in range(0, len(special_arr)):
        if is_char_need_escaping(special_arr[i]):
            special_arr[i] = "\\" + special_arr[i]
    return special_arr


# will check if a character needs escaping
def is_char_need_escaping(char):
    return char in '\[]()+$^*?..'
