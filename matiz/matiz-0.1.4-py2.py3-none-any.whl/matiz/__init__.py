import dataclasses

from . import _fields as fields
from ._common import dump_y, load_y
from ._contain import Containable, is_represented_as_mapping
from ._exceptions import BadYamlizDefinition, UnPythonizable, UnYamlizable
from ._fields import ValidableField
from ._fields_obsolete import GeneralFieldObsolete, ObsoleteNestableField
from ._serializ import Serializable
from ._valid import RangeValidator, Validable, Violation
from ._yamliz import ObsoleteAble, YamlizMeta, Yamlizable

"""
The reason for polymorphism used here is to provide different functionality 
coming from separate modules. 

It seems to be easier to maintain and vary it's behavior, 
making all the roles (capabilities) modular, delivered as Mixins.

"""


@dataclasses.dataclass
class Able(Validable, Serializable, Yamlizable, Containable):
    """Enjoy.

    E.G.:

    @dataclasses.dataclass
    class IndexableType(iz.Able):
        index: int = iz.fields.TInt8()
        value: int = iz.fields.TInt8()
        description: str = iz.fields.TString()

    """


__all__ = [
    'Able',
    'BadYamlizDefinition',
    'Containable',
    'dump_y',
    'fields',
    'GeneralFieldObsolete',
    'ValidableField',
    'load_y',
    'ObsoleteAble',
    'ObsoleteNestableField',
    'RangeValidator',
    'is_represented_as_mapping',
    'Serializable',
    'UnPythonizable',
    'UnYamlizable',
    'Validable',
    'Violation',
    'Yamlizable',
    'YamlizMeta',
]
