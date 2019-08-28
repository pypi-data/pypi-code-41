from typing import List, Union
from .group import Group
from .group import amharic_ones


class Number2WordsConverter(object):
    def __init__(self, lang: str = "am"):
        self._lang = lang
    def convert_positive_float(self, number, significant_digits=2):
        if not(isinstance(number, float)):
            raise ValueError("Float required required found: %s" % str(number))
        converter = _Float2WordsConverter(number, significant_digits=significant_digits, lang=self._lang)
        return converter.to_words(), converter.coma_separated
    
    def convert_positive_int(self, number):
        if not (isinstance(number, int) and number >= 0):
            raise ValueError("Positive integer required required found: %s" % str(number))
        converter = _Integer2WordsConverter(number, lang=self._lang)
        return converter.to_words(), converter.coma_separated
    def convert_negative_number(self, number, significant_digits=2):
        if not ((isinstance(number, int) or  isinstance(number, float)) and number<0):
            raise ValueError(
                "Negative number required found: %s" % str(number))
        converter = _Negative2WordsConverter(number, significant_digits=significant_digits, lang=self._lang)
        return converter.to_words(), converter.coma_separated
    def convert(self, number, significant_digits=2):
        """Converts number into  number's amharic word representation and comma seperated number	    
        >>> converter = Number2WordsConverter()
        >>> converter.convert(323)
        ("አንድ ሺህ ሁለት መቶ ሰላሳ አራት", "1,234")
        >>> converter.convert(2343.0)
        ("ሁለት ሺህ ሶስት መቶ አርባ ሶስት ነጥብ ዜሮ", "2,343.0")
        >>> converter.convert(-349343.934)
        ("ነጌትቭ ሶስት መቶ አርባ ዘጠኝ ሺህ ሶስት መቶ አርባ ሶስት ነጥብ ዘጠኝ ሶስት", "349,343.93")
        Arguments:
            number {int} -- Integer to be converted
        Returns:
            str -- Comma separeted representation of the number
        """
        if not (isinstance(number, int) or isinstance(number, float)):
            raise ValueError("Number required found: %s" % str(number))
            
        if number < 0:
            words, coma_separated = self.convert_negative_number(number)
        else:
            if isinstance(number, int):
                words, coma_separated = self.convert_positive_int(number)
            else:
                words, coma_separated = self.convert_positive_float(number, significant_digits=significant_digits)
        return words.strip(), coma_separated

class _Integer2WordsConverter(object):
    def __init__(self, number: int, lang: str = "am"):
        self._lang = lang
        coma_separated_numbers: str = self.number2CommaSeperatedString(number)
        
        group_list: List[str] = coma_separated_numbers.split(",")
        groups: List[Group] = []
        for i in range(len(group_list), 0, -1):
            g = group_list[i - 1]
            g_index = len(group_list) - i
            group = Group(g, g_index, lang=self._lang)
            groups.append(Group(g, g_index, lang=self._lang))
        self.coma_separated = coma_separated_numbers
        self.groups = groups

    def to_words(self):
        output = ""
        self.groups = self.remove_zeros()
        for i in range(len(self.groups)):
            if len(self.groups[i].to_words()) > 0:
                output = self.groups[i].to_words()+" " + output
        return output.replace("  ", " ")
    def remove_zeros(self):
        if len(self.groups) < 2:
            return self.groups
        else:
            output: List[Group] = []
            for i in range(len(self.groups)):
                if self.groups[i].to_words().strip() != "ዜሮ" and self.groups[i].to_words().strip() != "duwwaa":
                    output.append(self.groups[i])
            return output

    def number2CommaSeperatedString(self, number: int) -> str:
        """Converts integer into comma seperated number	    

        Arguments:
            number {int} -- Integer to be converted
        Returns:
            str -- Comma separeted representation of the number
        """
        if int(number) != number:
            raise ValueError("Number should be integer")
        num_str = str(number)
        output = ""
        for i in range(len(num_str), -1, -3):
            if i < 3 and i > 0:

                if output == "":
                    output = num_str[:i]
                else:
                    output = num_str[:i] + "," + output
            elif i > 0:
                if output == "":
                    output = num_str[i - 3:i]
                else:
                    output = num_str[i - 3:i] + "," + output
            else:
                continue
        return output


class _Float2WordsConverter(object):
    def __init__(self, number: float, significant_digits=2, lang: str = "am"):
        self._lang = lang
        integer_part: int = int(number)
        float_part = str(round(number - integer_part, significant_digits))
        self.significant_digits = significant_digits
        if number == integer_part:
            self.float_part = "0"
        else:
            index = float_part.find(".")
            if index != -1:
                self.float_part = float_part[index + 1:]

        coma_separated_numbers: str = self.int2CommaSeperatedString(
            integer_part)
        group_list: List[str] = coma_separated_numbers.split(",")
        groups: List[Group] = []
        for i in range(len(group_list), 0, -1):
            g = group_list[i - 1]
            g_index = len(group_list) - i
            group = Group(g, g_index, lang=self._lang)
            groups.append(Group(g, g_index, lang=self._lang))
        self.coma_separated = coma_separated_numbers + "." + str(self.float_part)
        self.int_groups = groups

    def to_words(self):
        output = ""
        self.int_groups = self.remove_zeros()
        for i in range(len(self.int_groups)):
            if len(self.int_groups[i].to_words()) > 0:
                output = self.int_groups[i].to_words()+" " + output
        integer_part = output.replace("  ", " ")
        if len(self.float_part) > 0:
            float_part = self.get_float_part_words().strip()
        else:
            float_part = ""

        if len(float_part) > 0:
            return integer_part.strip() + " ነጥብ " + float_part
        else:
            return integer_part

    def remove_zeros(self):
        if len(self.int_groups) < 2:
            return self.int_groups
        else:
            output: List[Group] = []
            for i in range(len(self.int_groups)):
                if self.int_groups[i].to_words().strip() != "ዜሮ"  and self.int_groups[i].to_words().strip() != "duwwaa":
                    output.append(self.int_groups[i])
            return output
    def get_float_part_words(self):
        output = ""
        for i in range(len(self.float_part)):
            output += amharic_ones[int(self.float_part[i])] + " "
        return output

    def int2CommaSeperatedString(self, number: int) -> str:
        """Converts integer into comma seperated number	    

        Arguments:
            number {int} -- Integer to be converted
        Returns:
            str -- Comma separeted representation of the number
        """
        if int(number) != number:
            raise ValueError("Number should be integer")
        num_str = str(number)
        output = ""
        for i in range(len(num_str), -1, -3):
            if i < 3 and i > 0:

                if output == "":
                    output = num_str[:i]
                else:
                    output = num_str[:i] + "," + output
            elif i > 0:
                if output == "":
                    output = num_str[i - 3:i]
                else:
                    output = num_str[i - 3:i] + "," + output
            else:
                continue
        return output


class _Negative2WordsConverter(object):
    def __init__(self, number: Union[int, float], significant_digits=2, lang: str = "am"):
        self._lang = lang
        self.converter: Union[_Integer2WordsConverter, _Float2WordsConverter]
        number = -number
        if isinstance(number, int):
            self.converter: _Integer2WordsConverter = _Integer2WordsConverter(
                number)
        elif isinstance(number, float):
            self.converter: _Float2WordsConverter = _Float2WordsConverter(number, significant_digits=significant_digits)
        self.coma_separated = self.converter.coma_separated
    def to_words(self):
        return "ነጌትቭ " + self.converter.to_words()
