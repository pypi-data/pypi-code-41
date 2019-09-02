from collections import abc

from more_itertools import pairwise

from .curve_source import CurveSource

__all__ = ['FunctionCurveSource', 'FunctionSection']


class FunctionSection:

    def __init__(self, domain_start, function):
        self.domain_start = domain_start
        self.function = function


class FunctionCurveSource(CurveSource):

    def __init__(self, sections, end_time):
        """
        sections is a sequence.
        """
        if not isinstance(sections, abc.Sequence):
            raise ValueError
        for a, b in pairwise(sections):
            if a.domain_start > b.domain_start:
                raise ValueError
        start_time = (sections[0].domain_start
                      if sections
                      else end_time)
        super().__init__(start_time, end_time)
        self.sections = sections

    def keys_and_times(self):
        for key, section in enumerate(self.sections):
            yield key, section.domain_start

    def get_value(self, key, time):
        this_section = self.sections[key]
        next_section = (self.sections[key + 1]
                        if len(self.sections) > key + 1
                        else None)
        if time < this_section.domain_start:
            raise ValueError(
                f"Time {time} is before {this_section.domain_start}.")
        if next_section is not None and time > next_section.domain_start:
            raise ValueError
        return this_section.function(time)

    def get_last_key(self):
        return 0
