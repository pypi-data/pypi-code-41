"""
    a description of a procedure
"""
from collections import OrderedDict
import inspect
import logging

LOGGER = logging.getLogger(__name__)


def describe(target):
    """
        Will inspect each function in target.__all__
        and return an instance of Procedure for each
    """
    result = OrderedDict()
    for key in target.__all__:
        f = getattr(target, key)
        s = Procedure(key, f)
        LOGGER.debug(s)
        result[key] = s
    return result


class Procedure:
    """
       a description of a procedure
    """

    def __init__(self, key, f):
        self.name = key
        self.desc = inspect.signature(f)
        self.docs = inspect.getdoc(f)
        self.f = f

    def __repr__(self):
        return f"{self.name} {self.desc} - {self.docs}"

    def parse_http_kwargs(self, values):
        """
            type conversion for int and float args
        """
        params = self.desc.parameters
        for k, v in values.items():
            if k in params and v is not None:
                if params[k].annotation is int:
                    values[k] = int(v)
                if params[k].annotation is float:
                    values[k] = float(v)

    @classmethod
    def annotation_to_str(cls, annotation):
        if annotation is None:
            return None
        if isinstance(annotation, str):
            return annotation
        if hasattr(annotation, "__name__"):
            return annotation.__name__
        return annotation

    def to_json(self):
        """ so it can be dumped """
        return OrderedDict(
            [
                ("name", self.name),
                ("params", [str(p) for p in self.desc.parameters.values()]),
                (
                    "returns",
                    self.annotation_to_str(self.desc.return_annotation)
                    if self.desc.return_annotation is not self.desc.empty
                    else "",
                ),
                ("docs", self.docs),
                ("auth", hasattr(self.f, 'auth')),
            ]
        )

