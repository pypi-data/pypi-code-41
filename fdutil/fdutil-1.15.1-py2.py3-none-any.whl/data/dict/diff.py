# encoding: utf-8


class DiffDict(object):

    """ http://code.activestate.com/recipes/576644-diff-two-dictionaries/#c7 """

    def __init__(self,
                 old,
                 new):

        self.old_dict = old
        self.new_dict = new

        self._old_set = set(self.old_dict.keys())
        self._new_set = set(self.new_dict.keys())

    @property
    def intersect(self):
        return self._new_set.intersection(self._old_set)

    @property
    def added(self):
        return self._new_set - self.intersect

    @property
    def removed(self):
        return self._old_set - self.intersect

    @property
    def changed(self):
        # TODO: is a deeper test for Mappings required?
        return set(o for o in self.intersect if self.old_dict[o] != self.new_dict[o])

    @property
    def unchanged(self):
        return set(o for o in self.intersect if self.old_dict[o] == self.new_dict[o])
