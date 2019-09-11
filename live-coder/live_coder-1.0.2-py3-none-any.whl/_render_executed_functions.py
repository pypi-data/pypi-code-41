
from ._function_output_objects import FunctionOutputObjects


def _add_to_file_functions(file_functions, func):
    if func.file_path not in file_functions:
        file_functions[func.file_path] = {}
    if func.name not in file_functions[func.file_path]:
        file_functions[func.file_path][func.name] = {
            'starting_line_number': func.line_number,
            'calls': {}
        }
    return file_functions

def render_executed_functions(executed_functions):
    '''
    Form explanation text as `block_lines` from change_bocks.

    params:
        executed function =
            ExecutedFunction
                .name = 'test'
                .file_path = 'src/main.py'
                .changes = [
                    Variable
                        .name = 'b'
                        .value = '120'
                    Function
                        .name = 'test'
                        .arguments = []
                        .reference_id = 1
                ]
                .reference_id = None

            ExecutedFunction
                .name = 'test'
                .file_path = 'src/main.py'
                .changes = [
                    Variable
                        .name = 'b'
                        .value = '0'
                ]
                .reference_id = 1
    returns:
        Variable changes, e.g:
            {
                'src/main.py': {
                    'test': {
                        'starting_line_number': 4,
                        'calls': {
                            'A': `function HTML`,
                            '5': `function HTML`
                        }
                    }
                }
            }
    '''
    file_functions = {}
    for func in executed_functions:
        file_functions = _add_to_file_functions(file_functions, func)
        parser = FunctionOutputObjects(func)
        func_output_lines = parser.run(func.line_number)
        func_html = func_output_lines.render()
        file_functions[func.file_path][func.name]['calls'][func.reference_id] = func_html
    return file_functions
