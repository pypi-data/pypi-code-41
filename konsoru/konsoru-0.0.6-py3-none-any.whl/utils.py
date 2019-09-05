from . import config


if config.system != 'windows':
    import termios, copy, readline

    class TerminalMode:
        NONECHO = 'nonecho'
        # NONCANONICAL = 'noncanonical'

        def __init__(self, mode):
            self._saved_attr = None
            self._mode = mode
            self._fd = None

        def __enter__(self):
            if self._mode == TerminalMode.NONECHO:
                self._fd = 0
                attr = termios.tcgetattr(self._fd)
                self._saved_attr = copy.deepcopy(attr)
                attr[3] &= ~termios.ECHO
                termios.tcsetattr(self._fd, termios.TCSANOW, attr)

        def __exit__(self, type, value, traceback):
            # restore previous terminal settings
            if self._saved_attr is not None:
                termios.tcsetattr(self._fd, termios.TCSANOW, self._saved_attr)


def enter_password(prompt='Password: ', hash_method=None):
    """
    Turns off echo and asks user password.

    Parameters
    ----------
    prompt : str
        A prompt message to show.
    hash_method : str or None
        If specified, hash the password and return the hash. Otherwise
        just return plain password. Supported methods are listed in the
        "algorithms_guaranteed" variable in hashlib module.

    Returns
    -------
    password : str
        Plaintext or hashed user input.
    """

    import hashlib, getpass
    password = getpass.getpass(prompt=prompt)
    if isinstance(hash_method, str):
        if hash_method not in hashlib.algorithms_guaranteed:
            raise ValueError('Unsupported hash method: %s' % hash_method)
        hash_method = getattr(hashlib, hash_method)
        hashobj = hash_method(password.encode())
        password = hashobj.hexdigest()
    elif hash_method is not None:
        raise ValueError("Parameter 'hash_method' must be a NoneType or str!")
    return password


def ask_user_input(prompt=''):
    """
    Ask user input (without being put into readline history).

    Parameters
    ----------
    prompt : str
        Prompt passed to input() function.
    """

    if config.system == 'windows':
        user_input = input(prompt)
    else:
        try:
            readline.set_auto_history(False)
            user_input = input(prompt)
        finally:
            readline.set_auto_history(True)
    return user_input


def ask_yes_or_no(prompt='Are you sure?'):
    """
    Ask yes or no until user explicitly answers and return True for yes, and
    False for no. User must answer with exactly matching yes or no, or a
    single character y or n. Answer is case insensitive.

    Parameters
    ----------
    prompt : str
        Message given to user. A "(y/n)" string is automatically appended to
        the end.

    Returns
    -------
    ans : bool
        True for yes, False for no.
    """
    prompt += ' (y/n) '
    while True:
        user_input = ask_user_input(prompt)
        user_input = user_input.lower()
        if user_input == 'yes' or user_input == 'y':
            return True
        elif user_input == 'no' or user_input == 'n':
            return False
