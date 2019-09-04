def string_to_ascii(string: str):
    """return string of ascii characters with _ as seperator"""
    return '_'.join(str(ord(c)) for c in string)


def ascii_to_string(string: str):
    """return ascii characters with _ as seperator to string"""
    return ''.join(chr(int(i)) for i in string.split('_'))
