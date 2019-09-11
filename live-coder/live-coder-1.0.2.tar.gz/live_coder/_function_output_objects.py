from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
import html

from ._change_classes import (
    ExecutedFunction,
    Loop,
    Variable,
    Print,
    Function,
    IfStatement,
    Error,
    Try
)
from ._output_objects import (
    OutputLines,
    OutputLoop
)


class FunctionOutputObjects:
    '''
        Converts an ExecutedFunction into an OutputLines object.
    '''

    def __init__(self, executed_function):
        self.func = executed_function
        self.vars = {}
        self._non_arg_i = None


    def _called_from_line(self):
        if self.func.parent:
            return '<span class="function_call_link mini_info" data-reference-id="{0}" data-reference-name="{1}">from {1}</span>'.format(
                self.func.parent.reference_id, self.func.parent.name
            )
        return ''

    def _func_args(self, changes):
        arg_strs = []
        i = 0
        for i, change in enumerate(changes):
            if type(change) is not Variable or change.is_arg == False:
                break
            if change.is_self:
                arg_strs.append('self')
            else:
                self.vars[change.name] = change.value
                value = '{0} = {1}'.format(change.name, change.value)
                arg_strs.append(self._colour_syntax(value))
        self._non_arg_i = i
        return arg_strs
    
    def _function_def_line(self):
        name_str = html.escape(self.func.name)
        arg_str = ', '.join( self._func_args(self.func.changes) )
        if self.func.reference_id:
            return '<span data-function-reference-id="{ref}">{name}</span>({args})'.format(name=name_str, args=arg_str, ref=self.func.reference_id)
        return '{name}({args})'.format(name=name_str, args=arg_str)


    @staticmethod
    def _obj_lineno(obj, start_lineno, last_lineno):
        if hasattr(obj, 'line_number'):
            return obj.line_number - start_lineno
        return last_lineno + 1


    def _lines_for_loop(self, start_lineno, loop):
        iterations = []
        for iteration_changes in loop.changes:
            func_html = self._lines_for_changes(start_lineno, iteration_changes)
            iterations.append(func_html)
        return [OutputLoop(iterations)]

    @staticmethod
    def _colour_syntax(code):
        if code:
            return highlight(code, PythonLexer(), HtmlFormatter())[:-1]
        return ''

    def _is_new_or_updated_variable(self, variable):
        return variable.name not in self.vars or self.vars[variable.name] != variable.value

    def _should_print_variable(self, variable):
        return self._is_new_or_updated_variable(variable) or variable.must_print

    def _line_for_variable(self, variable):
        if variable.name == 'return':
            code ='return {0}'.format(variable.value)
        elif self._should_print_variable(variable):
            self.vars[variable.name] = variable.value
            code = '{0} = {1}'.format(variable.name, variable.value)
        else:
            code = ''
        return self._colour_syntax(code)

    def _line_for_print(self, print_obj):
        args = [self._colour_syntax(v) for v in print_obj.values]
        return '<gray>print</gray> {0}'.format(', '.join(args))

    def _line_for_function(self, function_obj):
        arg_str = ', '.join([self._colour_syntax(v) for v in function_obj.arguments])
        if function_obj.reference_id:
            return '<gray class="function_call_link"><span class="function_call_link" data-reference-id="{0}" data-reference-name="{1}">{1}</span>({2})</gray>'.format(function_obj.reference_id, function_obj.name, arg_str)
        return '<gray>{0}({1})</gray>'.format(function_obj.name, arg_str)

    def _line_for_ifstatement(self, if_obj):
        code = self._colour_syntax(if_obj.code)
        return '<keyword>pass</keyword> <gray class="if_case">{0}</gray>'.format(code)

    @staticmethod
    def _line_for_error(error):
        if error.function_call_id:
            return '<span class="function_call_link" data-reference-id="{0}" data-reference-name="{1}">Exception caught at {1}</span>'.format(error.function_call_id, error.function_call_name)
        return '<error>ERROR</error> see Test Output for details'

    def _line_for_obj(self, obj):
        if type(obj) is Variable:
            return self._line_for_variable(obj)
        if type(obj) is Print:
            return self._line_for_print(obj)
        if type(obj) is Function:
            return self._line_for_function(obj)
        if type(obj) is IfStatement:
            return self._line_for_ifstatement(obj)
        if type(obj) is Error:
            return self._line_for_error(obj)
        raise Exception('Unknown basic object.')

    def _lines_for_changes(self, start_lineno, changes):
        last_lineno = -1
        output_lines = OutputLines([])
        for obj in changes:
            if type(obj) is Try:
                continue
            lineno = self._obj_lineno(obj, start_lineno, last_lineno)
            if type(obj) is Loop:
                lines = self._lines_for_loop(start_lineno + lineno, obj)
            else:
                lines = [self._line_for_obj(obj)]
            output_lines.set(lineno, lines)
            last_lineno = lineno
        return output_lines

    def _non_arg_changes(self):
        return self.func.changes[self._non_arg_i:]

    def _func_lines(self):
        called_from = self._called_from_line()
        func_def = self._function_def_line()
        return [func_def + called_from]

    def run(self, start_lineno):
        func_lines = self._func_lines()
        execution_lines = self._lines_for_changes(start_lineno + 1, self._non_arg_changes())
        return OutputLines(func_lines + execution_lines.lines)
