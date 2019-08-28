# vim:et:sta:sts=4:sw=4:ts=8:tw=79:
#
# Copyright (c) 2019 George Vlahavas
#
# Written by George Vlahavas <vlahavas@gmail.com>

__version__ = '0.1'


class TextConfig:
    """This is a class for managing simple configuration files with
    python. By simple, it means that they are simple text files,
    there are no sections and all options in the configuration files
    use a strict "OPTION=value" format, with no spaces between
    'OPTION', '=' and 'value'. The same 'OPTION' can be used more
    than once, so you can have multiple values.
    You can call it like this:
    from textconfig import TextConfig
    c = TextConfig('/path/to/configfile')
    """
    def __init__(self, configfile):
        self.configfile = configfile
        f = open(configfile, 'r')
        self.configopts = {}
        for line in f:
            # Yes, we don't read any commented out lines. We
            # might lose them afterwards when writing the
            # file, but I don't want to deal with that, it's
            # simpler this way.
            if line.lstrip(' ').startswith('#'):
                pass
            else:
                # also leave out any lines that are
                # obviously not config lines (they don't
                # have an = sign)
                if '=' in line:
                    option = line.partition('=')[0]
                    value = line.partition('=')[2].replace('\n', '')
                    self.add(option, value)
        f.close()

    def add(self, option, val):
        """Adds a new option/value pair. If there is no option with that name
        already, it creates the key in the dictionary. Otherwise, it appends
        the value to the existing list. Dictionary value is always a list.
        """
        if option not in self.configopts:
            self.configopts[option] = [val]
        else:
            self.configopts[option].append(val)

    def read(self):
        """Returns all options/values from the config file as a dictionary.
        NOTE: for Python versions < 3.6, the dictionary items will not be
        in the same order as they are read from the configuration file.
        """
        return self.configopts

    def get(self, option):
        """Returns the first matching option in the file.
        This will raise a KeyError if no keypair with the specified option
        exists.
        """
        return self.configopts[option][0]

    def get_all(self, option):
        """Returns a list of matching values for the specified option in the file.
        This will raise a KeyError if no keypair with the specified option
        exists.
        """
        return self.configopts[option]

    def change(self, option, oldval, newval):
        """Changes an old value of an option to a new value. If there are
        multiple occurences, it will change all of them.
        Raises a ValueError if there is no match for option/oldval.
        """
        found = False
        for i, val in enumerate(self.configopts[option]):
            if val == oldval:
                self.configopts[option][i] = newval
                found = True
        if not found:
            raise ValueError('No option with the name {opt} and value {val}'
                    .format(opt=option, val=oldval))

    def set(self, option, newval):
        """Assigns a new value to an existing option. If there
        are multiple options with the same name, it will only
        change the first occurence.
        This will raise a KeyError if no keypair with the specified option
        exists.
        """
        self.configopts[option][0] = newval

    def remove(self, option, value):
        """Remove an option/value pair from the config. If there
        are multiple occurences it will remove all of them.
        This will raise a KeyError if no keypair with the specified option
        exists.
        Raises a ValueError if there is no match for the
        option/value pair.
        """
        found = False
        for i, val in enumerate(self.configopts[option]):
            if val == value:
                found = True
        if not found:
            raise ValueError('No option with the name {opt} and value {val}'
                    .format(opt=option, val=value))
        self.configopts[option] = [i for i in self.configopts[option] if i != value]
        if not self.configopts[option]:
            self.configopts.pop(option)

    def remove_all(self, option):
        """Removes an option from the config. If multiple
        instances are found, it deletes all of them.
        This will raise a KeyError if no keypair with the specified option
        exists.
        """
        self.configopts.pop(option)

    def write(self):
        """Writes configuration options back to the file."""
        with open(self.configfile, "w") as f:
            for key in self.configopts:
                for val in self.configopts[key]:
                    f.write('{opt}={val}\n'.format(opt=key,val=val))

