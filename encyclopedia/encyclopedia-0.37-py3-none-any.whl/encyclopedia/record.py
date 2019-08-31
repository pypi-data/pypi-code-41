# standard
import unittest
import types
import sys
from collections import Mapping
# external
# internal
from encyclopedia.dictionary import Dictionary
from encyclopedia.templates import Unindexed

class Record_Exception(Exception):
    pass

class Record(dict, Unindexed):
    '''
    A factory creating Encyclopedia-ified Dictionaries with:

    - restricted keys
    - automatic type conversions
    - optional defaults
    '''

    def __init__(self, mapping=None, autopopulate=False, restrict=True):
        Unindexed.__init__(self, frozen=False, mapping=mapping)
        self.autopopulate = autopopulate
        self.restrict = restrict

    def __setitem__(self, key, value):
        assert isinstance(value, types.FunctionType)
        value()  # assert it works with no parameters
        return dict.__setitem__(self, key, value)

    @staticmethod
    def missing(key):
        raise Record_Exception("Missing record key:" + key)

    def instance(self):
        '''
        create an individual (Record) instance
        '''

        class Internal(Dictionary):

            def __init__(dictionary, mapping=None):
                Dictionary.__init__(dictionary)
                if self.autopopulate:
                    for key in self:
                        dictionary[key] = self[key]()
                if mapping is not None and isinstance(mapping, Mapping):
                    for key in mapping:
                        dictionary[key] = mapping[key]

            def __setitem__(dictionary, key, value):
                if key not in self and self.restrict:
                    Record.missing(key)
                elif key not in self and not self.restrict:
                    dict.__setitem__(dictionary, key, value) # set directly
                elif key in self:
                    dict.__setitem__(dictionary, key, self[key](value)) # cast type
                else:
                    assert False

        return Internal

class Test_Record(unittest.TestCase):

    def setUp(self):

        def noname(x=None, default='ANONYMOUS'):
            if x is None:
                return default
            else:
                return str(x)

        record = Record({
            'coat': str,
            'tail':int,
            'name':noname,
            'age':float,
            'height':float
            },
            autopopulate=True
            )
        self.record = record
        self.Dog = record.instance()

    def test_defaults(self):
        harley = self.Dog({'height':11})
        assert len(harley) == len(self.Dog()) # because it's autopopulated
        assert harley['height'] == 11
        assert harley['tail'] == 0
        assert harley['name'] == 'ANONYMOUS'
        harley['name'] = 'Mr. Rascal'
        assert harley['name'] == 'Mr. Rascal'
        assert harley['age'] == 0

    def test_basic(self):
        '''
        test basic functions of Record
        '''
        harley = self.Dog()
        harley['tail'] = 3
        assert harley['tail'] == 3

    def test_restrict(self):
        attributes = {
            'coat': str,
            'tail':int,
            'age':float,
            'height':float
            }

        Purebred = Record(
            attributes,
            autopopulate=True,
            restrict=True
            ).instance()

        harley = Purebred({'coat':'brown'})
        harley['tail'] = 3
        assert harley['tail'] == 3

        try:
            harley['teeth'] = 5 # this is not a valid key
            assert False
        except Record_Exception:
            pass

        Mutt = Record(
            attributes,
            autopopulate=True,
            restrict=False
            ).instance()

        harley = Mutt({'coat':'brown', 'demeanor':'feisty'})
        assert harley['demeanor'] == 'feisty'
        harley['tail'] = 3
        assert harley['tail'] == 3
        harley['teeth'] = 12 # this is not a valid key
        assert harley['teeth'] == 12

    def test_sizing(self):
        '''
        assure that the resultant record/dictionaries do not chew up memory unnecessarily

        Note: can also use https://pypi.python.org/pypi/Pympler to confirm this but instead
        chose to minimize external dependencies
        '''
        n = 10**4
        keys = range(1, n)
        record = Record({key:int for key in keys}).instance()()
        dictionary = {}
        for i in range(1, n):
            record[i] = i
            dictionary[i] = i
        assert sys.getsizeof(record) - sys.getsizeof(dictionary) < 20 # bytes

if __name__ == '__main__':
    unittest.main()
