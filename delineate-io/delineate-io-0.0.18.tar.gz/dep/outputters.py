class ConsoleOutputter(object):
    """ConsoleOutputter writes the result to the console"""

    def output(self, result):
        """Prints to the console
        
        Args:
            result (object): The result of the assessment to be output
        """  
        
        print()
        print(result)
        print()


class FileOutputter(object):
    """FileOutputter writes the result to a specified file"""

    def __init__(self, file_name):
        """Initializes the FileOutputter

        Args:
            file_name (str): Name of the file to output
        """

        self.file_name = file_name
        

    def output(self, formatted_result):
        """Outputs the results to a file
        
        Args:
            formatted_result (object): The result of the assessment to be output
        """

        with open(self.file_name, 'w') as file:
            file.write(formatted_result)
