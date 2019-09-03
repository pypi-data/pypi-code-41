from influxed.orm.capabilities.executable import Executable
from influxed.ifql import show

class Showable(Executable):
    """
        Definition of a object that can initiate a show query
    """
    def __show_builder__(self, keyword):
        return show(keyword, hook=self)

    def __show_prefix__(self, show_statement):
        return show_statement

    def show(self, keyword=None):
        """
            Function for initiating a show query
        """
        return self.__show_prefix__(self.__show_builder__(keyword))
