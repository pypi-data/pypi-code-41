import dill
from brainiac.abstract_model import AbstractModel
from typing import List
from brainiac.protos.brainiac_pb2 import Row


def to_correct_type(s):
    try:
        return float(s)
    except ValueError:
        return s


def convert_rows_to_array(x: List[Row]):
    return [[to_correct_type(point) for point in row.points] for row in x]


def package(some_class, file=None, write_to_file=True):
    # type: (AbstractModel, str, bool) -> bytes
    dill.settings['recurse'] = True
    if file is not None:
        name = file.split("/")[-1]
        if not name == "script.pkl":
            file = "script.pkl"
    else:
        file = "script.pkl"
    if write_to_file:
        with open(file, 'wb') as f:
            dill.dump(some_class, f)
        return None
    else:
        return dill.dumps(some_class)


__all__ = ["package"]
