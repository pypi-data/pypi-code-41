from p10s.values import value
from pathlib import Path


class BaseContext():
    def __init__(self, input=None, output=None):
        if input is None:
            self.input = value('p10s', {}).get('file', None)
        else:
            self.input = Path(input)

        if output is not None:
            self.output = Path(output)
        elif self.input is not None:
            self.output = self.input.with_suffix(self.output_file_extension)
        else:
            self.output = None

    def render(self):
        raise NotImplementedError()  # pragma: no cover

    def _output_stream(self):
        self.output.parent.mkdir(parents=True, exist_ok=True)
        return self.output.open("w")

    def __repr__(self):
        return "<" + self.__module__ + "." + self.__class__.__name__ + ">"
