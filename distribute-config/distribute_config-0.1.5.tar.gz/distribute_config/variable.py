class Variable:
    """A config variable
    """

    def __init__(self, name, default, description, type, is_list=False, possible_values=None):
        # Variable name, used as key in yaml, or to get variable via command line and env varaibles
        self.name = name

        # Description of the variable, used for --help
        self.description = description

        # Type of the variable, can be int, float, str
        self.type = type
        self.is_list = is_list

        # The value of the variable
        self._value = None
        self._possible_values = possible_values
        self.set_value(default)

    def __str__(self):
        return f"name: {self.name}"

    def get_value(self):
        return self._value

    def set_value(self, value):
        """Check if the value match the type of the variable and set it

        Args:
            value: The new value of the variable, will be checked before updating the var 

        Raises:
            TypeError: if the type of value doesn't matche the type of the variable
        """
        if type(self._possible_values) is list:
            assert value in self._possible_values, f"{value} need to be inside {self._possible_values}"

        if self.is_list:
            assert type(value) == list, str(value) + " is not a list"
            end_list = []
            for element in value:
                end_list.append(self._convert_type(element))
            self._value = end_list
        else:
            self._value = self._convert_type(value)

    def _convert_type(self, value):
        # str and float values can be parsed without issues in all cases
        if self.type in [str, float]:
            return self.type(value)
        if self.type == int:
            return self._convert_type_int(value)
        if self.type == bool:
            return self._convert_type_bool(value)
        return value

    def _convert_type_int(self, value):
        """convert a value in any data type to int

        Args:
            value: a value read from the json file or from python or from the command line

        Raises:
            ValueError: [description]
        """
        if type(value) == str:
            value = float(value)
        if type(value) == float:
            if int(value) == value:
                value = int(value)
            else:
                raise ValueError("value should have type {} but have type {}".format(self.type, type(value)))
        return value

    def _convert_type_bool(self, value):
        if type(value) == str:
            if value.lower() == "true":
                return True
            if value.lower() == "false":
                return False
            raise ValueError(f"Can't parse boolean {value}")
        return bool(value)
