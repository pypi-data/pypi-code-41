import json
import os
from edaphic.wipy_utilities import get_timestamp


class MurdMemory(dict):
    required_keys = ["ROW", "COL"]

    def __init__(self, **kwargs):
        self = kwargs
        for req_key in MurdMemory.required_keys:
            if req_key not in self:
                raise Exception("{} must be defined".format(req_key))

        for key, value in self.items():
            self[key] = json.dumps(value) if not isinstance(value, str) else value


class Murd:
    """ Murd represents a collection of matrix-like memory structures
        stored in a key-value store system. Initial storage system backends
        are:
            Primary: String
            Secondary: DynamoDB
            Tertiary: S3, local filestore

        Challenges:
            Primary:
                * Table Creation
                * Simultanenous Request

            Secondary/Tertiary:
                * Optimize file system (directory, folder, contents) for S3 or
                  locally managed key-value store
    """

    row_col_sep = "|||||"

    def __init__(
        self,
        name='',
        murd='{}',
        murds=[],
        **kwargs
    ):
        if name == '':
            name = 'murd'
        self.name = name

        self.murd = murd
        self.murds = murds
        self.murds.append(self)

    @staticmethod
    def prime_mems(mems):
        return list({(MurdMemory(**ob)['ROW'], MurdMemory(**ob)['COL']): ob for ob in mems}.values())

    @staticmethod
    def mem_to_key(mem):
        return "{}{}{}".format(mem['ROW'], Murd.row_col_sep, mem['COL'])

    @staticmethod
    def row_col_to_key(row, col):
        return "{}{}{}".format(row, Murd.row_col_sep, col)

    def update(
        self,
        mems,
        identifier="Unidentified"
    ):
        primed_mems = self.prime_mems(mems)
        creationstamp_string = get_timestamp()

        murd = json.loads(self.murd)

        if len(primed_mems) > 0:
            print("Storing {} mems".format(len(primed_mems)))

            for count, memory in enumerate(primed_mems):
                memory['CREATIONSTAMP'] = creationstamp_string
                murd[self.mem_to_key(memory)] = memory

        self.murd = json.dumps(murd)

    def local_read(
        self,
        row,
        col=None,
        greater_than_col=None,
        less_than_col=None,
        **kwargs
    ):
        murd = json.loads(self.murd)

        keys = list(murd.keys())
        prefix = "{}{}".format(row, Murd.row_col_sep)

        matched = [key for key in keys if prefix in key]

        if col is not None:
            col_prefix = "{}{}".format(prefix, col)
            matched = [match for match in matched if col_prefix in match] 

        # Filter out lower than less_than_col keys
        if less_than_col is not None:
            lowest_prefix = "{}{}".format(prefix, less_than_col)
            matched = [match for match in matched if lowest_prefix < match]

        # Filter out greater than greater_than_col keys
        if greater_than_col is not None:
            greatest_prefix = "{}{}".format(prefix, greater_than_col)
            matched = [match for match in matched if greatest_prefix > match]

        # Create MurdMemory objects for results
        results = [MurdMemory(**murd[key]) for key in matched]

        if 'Limit' in kwargs:
            results = results[:int(kwargs['Limit'])]

        return results

    def read(
        self,
        row,
        col=None,
        greater_than_col=None,
        less_than_col=None,
        **kwargs,
    ):
        if type(row) is list:
            arg_sets = []
            rows = row
            for row in rows:
                arg_kwargs = {key: value for key, value in kwargs.items()}
                arg_kwargs['row'] = row
                arg_kwargs['col'] = col
                arg_kwargs['less_than_col'] = row
                arg_kwargs['greater_than_col'] = greater_than_col
                arg_sets.append(arg_kwargs)

            results = [self.read(**arg_set) for arg_set in arg_sets]
            memory_rows = {arg_set['row']: mem for arg_set, mem in results}

            return memory_rows
        else:
            arg_set = {key: value for key, value in kwargs.items()}
            arg_set['row'] = row
            arg_set['less_than_col'] = less_than_col
            arg_set['greater_than_col'] = greater_than_col

            results = []
            for murd in self.murds:
                murd_results = murd.local_read(**arg_set)
                results.extend(murd_results)

            return results

    def delete(self, mems):
        murd = json.loads(self.murd)
        primed_mems = self.prime_mems(mems)
        keys = [self.mem_to_key(m) for m in primed_mems]
        for key in keys:
            if key not in Murd:
                raise Exception("MurdMemory {} not found!".format(key))

        for key in keys:
            murd.pop(key)

        self.murd = json.dumps(murd)

    def assimilate(
        self,
        foriegn_murd
    ):
        """ Become aware of other Murd so as to read it as well """
        self.murds.append(foriegn_murd)

    def absorb(
        self,
        foriegn_murd
    ):
        pass

    def __str__(self):
        return self.murd
