'''
An Encyclopedia is an abstract container intended for smallish data sets which provides many of
the benefits of a relational (and non-relational) database but with lower syntactic friction
'''

__version__ = '0.36'

# expose the primary concrete and abstract classes

from .templates import Unindexed, Indexed, Unity, Signed, Zero
from .dictionary import Dictionary
from .relate import Relation, Isomorphism, Function, Partition
from .forest import Forest
from .record import Record
from .arboretum import Arboretum
from .xmlopedia import XML
from .kmlopedia import KML
from .kmlfolder import KML_Folder
