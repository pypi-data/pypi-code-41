
amharic_ones = ["ዜሮ", "አንድ", "ሁለት", "ሶስት",
                "አራት", "አምስት", "ስድስት", "ሰባት", "ስምንት", "ዘጠኝ"]
amharic_tens = ["አስራ", "ሃያ", "ሰላሳ", "አርባ", "ሃምሳ", "ስልሳ", "ሰባ", "ሰማንያ", "ዘጠና"]
amharic_powers = ["ሺህ", "ሚሊዮን", "ቢሊዮን", "ትሪሊዮን"]

ao_ones = ["duwwaa", "tokko", "lama", "sadii", "afuri", "shani", "jaha", "torba", "saddeeti", "sagali"]
ao_tens = ["Kudha", "digdami", "soddomi", "afurtami", "shantami", "jahatami", "torbaatami", "saddeetami", "sagaltami"]
ao_powers = ["kuma", "kitila", "biliyoonii", "triliyoonii"]

def is_digits(string: str) -> bool:
    """Checks if a given string is composed of only digits
    >>> is_digits("123")
    True
    >>> is_digits("abc")
    False
    >>> is_digits("3434a")
    False
    Arguments:
        string {str} -- String to be checked
    
    Returns:
        bool -- True if the string is composed of only digits,  else False
    """

    output: bool = False
    try:
        num: int = int(string)
        output = True
    except ValueError as e:
        output = False
    return output


class Group(object):
    """Datastructure to represent group of digits. It is assumed that the numbers are grouped in natural way of writing numbers by grouping into three digits
    and seperating them by commas. E.g 1,343,641,234. Group index is obtained the index of the group from right to left.
    E.g in "1,343,641,234", Group index(g_index) of "343" is 2.
    >>> g = Group("343", 1)
    >>> g.value
    "343"
    >>> g.
    >>> g = Group("", 0)
    ValueError      Traceback (most recent call last)
        ...
    ValueError: Value should be composed of only digits
    >>> g = Group("abc", 3)
    ValueError      Traceback (most recent call last)
        ...
    ValueError: Value should be composed of only digits
    >>> g = Group("32c", 1)
    ValueError      Traceback (most recent call last)
        ...
    ValueError: Value should be composed of only digits
    >>> g = Group("32", -1)
    ValueError      Traceback (most recent call last)
        ...
    ValueError: g_index should be non-negative integer
    """

    def __init__(self, value: str, g_index: int, lang:str="am"):
        """Provides Group initialization
        
        Arguments:
            value {str} -- Group string value
            g_index{int} -- Group index. Group index is obtained group index counted from right to left, when the number is seperated by commas.
        """

        self.value = value
        self.g_index = g_index
        self._lang = lang
        
        assert self._lang in ["am", "ao"], "Currently supported languages are only: '%s' and '%s'"%("am", "ao")

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        if not is_digits(value):
            raise ValueError("Value should be composed of only digits")
        elif len(value) > 3 or len(value) == 0:
            raise ValueError(
                "Value length should be between 1 and 3 inclusive")
        self._value = self.remove_trailing_zeros(value)

    @property
    def g_index(self):
        return self._g_index

    @g_index.setter
    def g_index(self, g_index: int) -> None:
        if int(g_index) != g_index or g_index < 0:
            raise ValueError("g_index should be non-negative integer")
        self._g_index = g_index

    def remove_trailing_zeros(self, group: str) -> str:
        """Removes prefix zeros. When written in word numbers are often grouped and seperated by commas.
        >>> remove_trailing_zeros("012")
        12
        >>> remove_trailing_zeros("000")
        0
        >>> remove_trailing_zeros("123")
        123
        >>> remove_trailing_zeros("3434343")
        ValueError      Traceback (most recent call last)
            ...
        ValueError: Group length should be between 1 and 3 inclusive
        >>> remove_trailing_zeros("23a")
        ValueError      Traceback (most recent call last)
            ...
        ValueError: Group should be number

        Arguments:
            group {str} -- Group of numbers.
        
        Raises:
            ValueError -- If the given group is not number
            ValueError -- If the length of the group is either zero or greater than 3. It is assumed that the numbers are often grouped at least one and at most three.

        
        Returns:
            str -- Group with prefix zeros are being removed
        """

        while len(group) > 1 and group[0] == "0":
            group = group[1:]
        return group

    def get_ones(self):
        """Get the ones place word representation of current group
        >>> a = Group("123", 0)
        >>> a.get_ones()
        ሶስት
        >>> b = Group("0", 0)
        >>> b.get_ones()
        ዜሮ
        Returns:
            str -- Ones place word representation of current group if the group has ones place
        """

        if self.value[-1] == "0" and len(self.value) > 1:
            return ""
        else:
            if self._lang=="am":
                return amharic_ones[int(self.value[-1])]
            elif self._lang == "ao":
                return ao_ones[int(self.value[-1])]
            

    def get_tens(self):
        """Get the tens place word representation of current group
        >>> a = Group("0", 0)
        >>> a.get_tens()
        
        >>> b = Group("2", 0)
        >>> b.get_tens()
        
        >>> c = Group("20", 0)
        >>> c.get_tens()
        ሃያ
        >>> d = Group("102", 0)
        >>> d.get_tens()
        
        >>> d = Group("110", 0)
        >>> d.get_tens()
        አስር
        >>> d = Group("114", 0)
        >>> d.get_tens()
        አስራ

        Returns:
            str -- Tens place word representation of current group if the group has tens place
        """
        if len(self.value) < 2 or self.value[-2] == "0":
            return ""
        else:
            if self.value[-1] == "0" and self.value[-2] == "1":
                if self._lang=="am":
                    return "አስር"
                elif self._lang=="ao":
                    return "kudhan"
            
            if self._lang == "am":
                return amharic_tens[int(self.value[-2]) - 1]
            elif self._lang == "ao":
                if self.value[-1] != "0":
                    return ao_tens[int(self.value[-2]) - 1]
                else:
                    return ao_tens[int(self.value[-2]) - 1][:-1]+"a"



    def get_hundreds(self):
        """Get the hundreds place word representation of current group
        >>> a = Group("0", 0)
        >>> a.get_hundreds()

        >>> b = Group("12", 0)
        >>> b.get_hundreds()

        >>> c = Group("100", 0)
        >>> c.get_hundreds()
        አንድ መቶ

        Returns:
            str -- Hundreds place word representation of current group if the group has hundreds place
        """
        if not is_digits(self.value):
            raise ValueError("Group should be number")
        if len(self.value) < 3:
            return ""
        else:
            if self._lang=="am":
                return amharic_ones[int(self.value[-3])] + " መቶ"
            elif self._lang=="ao":
                return "dhibba "+ ao_ones[int(self.value[-3])]+" fi"

    def to_words(self) -> str:
        """Converts current group into word representation
        >>> g = Group(341)
        >>> g.to_words()
        ሶስት መቶ አርባ አንድ
        Returns:
            str -- Word representation of the group
        """
        output = ""
        hundreds = self.get_hundreds()
        tens = self.get_tens()
        ones = self.get_ones()
        if len(hundreds) > 0:
            output += hundreds
        if len(tens) > 0:
            if len(hundreds) > 0:
                output+=" "
            output +=  tens
        if len(ones) > 0:
            if len(tens) > 0:
                output += " "
            elif len(hundreds) > 0:
                output+=" "
            output += ones
        power = self.get_power()
        if len(power) > 0:
            
            if output == "ዜሮ" or output == "duwwaa":
                output = ""
            else:
                if self._lang=="am":
                    output = output + " " + power
                elif self._lang == "ao":
                    output = power + " " + output+" fi,"
                    

        return output
    def get_power(self):
        if self.g_index == 0:
            return ""
        else:
            if self._lang=="am":
                return amharic_powers[self.g_index - 1]
            elif self._lang == "ao":
                return ao_powers[self.g_index - 1]
                
            
