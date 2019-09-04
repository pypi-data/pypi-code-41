from prompt_toolkit import (
    prompt,
    print_formatted_text as pprint,
    HTML
)
from prompt_toolkit.completion import FuzzyWordCompleter, Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError


class FunctionValidator(Validator):

    def __init__(self, methods):
        self.methods = methods + ['q']
        return Validator.__init__(self)

    def validate(self, document):
        text = document.text
        if text not in self.methods:
            raise ValidationError(message='Pick a test class.', cursor_position=0)


class MyCustomCompleter(Completer):
    def get_completions(self, document, complete_event):
        yield Completion('completion', start_position=0)


def _format_test_classes(test_classes):
    formatted_test_classes = []
    for test_class in test_classes:
        class_id = test_class.id
        id_parts = class_id.split('.')
        class_name = id_parts[-1]
        class_path = id_parts[:-1]
        formatted_test_classes.append(
            class_name + ' '*4 + '.'.join(class_path) + '.py'
        )
    return formatted_test_classes

def pick_a_test_class(test_classes):
    formatted_test_classes = _format_test_classes(test_classes)
    html_completer = FuzzyWordCompleter(formatted_test_classes)
    picked_method = prompt(
        'Enter test class name: ',
        completer=html_completer,
        complete_while_typing=True,
        validator=FunctionValidator(formatted_test_classes),
    )
    if picked_method == 'q':
        quit()
    return test_classes[formatted_test_classes.index(picked_method)]
