
class ExecutedFunction:
    '''
        Represent the execution of a function.

        .name = the function name
        .changes = list of change values
    '''
    def __init__(self, name, file_path, line_number, changes):
        self.name = name
        self.file_path = file_path
        self.line_number = line_number
        self.changes = changes
        self.reference_id = None

class Loop:
    '''
        Represent the values from a loop (for, while, etc)

        .id = unique loop id
        .changes = list of lists of change values (one list for each iteration)
    '''
    def __init__(self, loop_id, line_number, iterations_change_blocks):
        self.id = loop_id
        self.line_number = line_number
        self.changes = iterations_change_blocks

class Variable:
    '''
        Represents a Variable.
    '''
    def __init__(self, name, value, line_number, is_arg, must_print, is_self):
        self.name = name
        self.value = value
        self.line_number = line_number
        self.is_arg = is_arg
        self.must_print = must_print
        self.is_self = is_self

class Print:
    '''
        Represents a print statement.

        .values = list of values printed
    '''
    def __init__(self, values, line_number):
        self.values = values
        self.line_number = line_number

class Function:
    '''
        Represents a Function call.
    '''
    def __init__(self, name, arguments, line_number):
        self.name = name
        self.arguments = arguments
        self.reference_id = None
        self.line_number = line_number

class IfStatement:
    '''
        Represent an if statement.

        .code = "elif z == 1:"
    '''
    def __init__(self, code, line_number):
        self.code = code
        self.line_number = line_number

class Error:
    '''
        Represents execution being stopped by an exception.
    '''
    def __init__(self):
        pass
