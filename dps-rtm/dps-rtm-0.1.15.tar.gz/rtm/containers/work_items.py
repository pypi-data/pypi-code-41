# --- Standard Library Imports ------------------------------------------------
import collections
from typing import List

# --- Third Party Imports -----------------------------------------------------
# None

# --- Intra-Package Imports ---------------------------------------------------
from rtm.containers.fields import CascadeBlock
import rtm.main.context_managers as context
from rtm.main.exceptions import UninitializedError
from rtm.validate.checks import cell_empty


class WorkItem:

    def __init__(self, index_):
        self.index = index_
        # work item's vertical position relative to other work items
        # contrast with position, which is which cascade column is marked
        self.cascade_block_contents = OrderedDictList()
        self._parent = UninitializedError()

    def has_parent(self):
        if self.parent is None:
            return False
        elif self.parent >= 0:
            return True
        else:
            return False

    def set_cascade_block_row(self, cascade_block_row: list):
        for index_, value_ in enumerate(cascade_block_row):
            if not cell_empty(value_):
                self.cascade_block_contents[index_] = value_

    @property
    def position(self):
        try:
            return self.cascade_block_contents.get_first_key()
        except IndexError:
            return None

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value_):
        self._parent = value_

    def find_parent(self, work_items):

        # set default
        self.parent = None

        if self.position is None:
            # If no position (row was blank), then no parent
            return
        elif self.position == 0:
            # If in first position, then it's the trunk of a tree!
            self.parent = -1
            return

        # Search back through previous work items
        for index_ in reversed(range(self.index)):

            other = work_items[index_]

            if other.position is None:
                # Skip work items that have a blank cascade. Keep looking.
                continue
            elif other.position == self.position:
                # same position, same parent
                self.parent = other.parent
                return
            elif other.position == self.position - 1:
                # one column to the left; that work item IS the parent
                self.parent = other.index
                return
            elif other.position < self.position - 1:
                # cur_work_item is too far to the left. There's a gap in the chain. No parent
                return
            else:
                # self.position < other.position
                # Skip work items that come later in the cascade. Keep looking.
                continue


class WorkItems(collections.abc.Sequence):

    def __init__(self):

        # --- Get Cascade Block -----------------------------------------------
        fields = context.fields.get()
        cascade_block = fields.get_matching_field(CascadeBlock)
        cascade_block_body = cascade_block.get_body()

        # --- Initialize Work Items -------------------------------------------
        self._work_items = [WorkItem(index_) for index_ in range(fields.body_length)]
        for work_item in self:
            row_data = get_row(cascade_block_body, work_item.index)
            work_item.set_cascade_block_row(row_data)
            work_item.find_parent(self._work_items)

    def __getitem__(self, item) -> WorkItem:
        return self._work_items[item]

    def __len__(self) -> int:
        return len(self._work_items)


class OrderedDictList(collections.OrderedDict):
    def value_at_index(self, index_: int):
        try:
            return list(self.values())[index_]
        except IndexError:
            raise IndexError("OrderedDictList index_ out of range")

    def get_first_key(self):
        try:
            return list(self.keys())[0]
        except IndexError:
            return None

    def get_first_value(self):
        first_key = self.get_first_key()
        if first_key is None:
            return None
        return self[first_key]


def get_row(columns: List[list], index_: int) -> list:
    return [col[index_] for col in columns]


if __name__ == "__main__":
    pass
