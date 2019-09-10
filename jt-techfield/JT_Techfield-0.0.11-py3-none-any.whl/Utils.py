"""
Jacob Thompson

Utils
"""
import numpy as np
from matplotlib import pyplot as plot
from skimage.transform import resize
import time

class Timer:
    def __init__(self):
        self.start_time = time.time()

    def tic(self):
        self.start_time = time.time()

    def toc(self):
        return time.time() - self.start_time


def ImagePad(image, padding):
    image_padded = np.pad(image, ((padding, padding), (padding, padding), (0, 0)), mode='constant',
                        constant_values=0)
    return image_padded

def LoadImage(path, size = None):
    image = plot.imread(path).copy()
    if not size is None:
        image = resize(image, output_shape = size)

    image = np.swapaxes(image, 0, 2)
    image[0] = np.flip(image, 0)
    return image

def ProgressBar(percent, size = 15):
    """
    Generates a progress bar string that is useful for tracking progress.

    :param percent: Percentage of the bar to be filled in.
    :param size: Size of the bar (how many characters long should the bar be?).
    :return: A string containing the progress bar.
    """
    done_chars = int(min(max(percent, 0), 1) * size)
    left_chars = size - done_chars
    return '|' + chr(9608) * done_chars + ' ' * left_chars + '|'


class TimeList(list):
    def __init__(self, iterable=()):
        """
        This is a simple wrapper class for a list that will also keep track of the time when an element was added to the
        list.

        This list has two additional attributes:
            TimeList.time: The time that each value was added to the list.
            TimeList.duration: The time that each value was added to the list since the list was created.

        :param iterable: Initial iterable to populate the list
        """
        self.start_time = time.time()
        super().__init__(iterable)
        if iterable:
            self.time = [self.start_time] * len(self)
            self.duration = [0.] * len(self)
        else:
            self.time = []
            self.duration = []
        self.dur = self.duration

    def __setitem__(self, key, value):
        """
        Set self[key] to value.

        Keeps track of when the value gets set.

        :param key: Where to set the value
        :param value: What to set the value to.
        :return:
        """
        current = time.time()
        self[key] = value
        self.time[key] = current
        self.duration[key] = current - self.start_time

    def append(self, item):
        """
        Appends an object to the end of the list.

        Keeps track of the time the item was added.

        :param item: Item to append to the list
        :return:
        """
        current = time.time()
        super().append(item)
        self.time.append(current)
        self.duration.append(current - self.start_time)

    def extend(self, iterable):
        """
        Extend list by appending elements from the iterable.

        Keeps track of the time the items are extended.

        :param iterable: Iterable to be added to the list
        :return:
        """
        current = time.time()
        super().extend(iterable)
        added = len(self) - len(self.time)
        self.time.extend([current] * added)
        self.duration.extend([current - self.start_time] * added)

    def pop(self, index: int = ...):
        """
        Remove and return item at index (default last).
        Raises IndexError if list is empty or index is out of range.

        :param index: Index to remove the item from.
        :return:
        """
        super().pop(index)
        self.time.pop(index)
        self.duration.pop(index)


    def insert(self, index, obj):
        """
        Insert object before index.

        Keeps track of the time the item was inserted.

        :param index: Index of the list to add before.
        :param obj: Object to insert into the list.
        :return:
        """
        current = time.time()
        super().insert(index, obj)
        self.time.insert(index, current)
        self.duration.insert(index, current - self.start_time)

    def remove(self, value):
        """
        Remove first occurrence of value.
        Raises ValueError if the value is not present.

        :param value: Value to remove.
        :return:
        """
        i = self.index(value)
        super().remove(value)
        self.time.pop(i)
        self.duration.pop(i)



def RecGetattr(obj, name):
    """
    A beefier version of the builtin getattr() that can get sub attributes - attributes of attributes.

    Accomplishes this by recursively calling itself.

    :param obj: Object to get the attribute from.
    :param name: Name of the attribute to get including any parent attributes. Should be in the form of: "parent.parent.attribute"
    :return: The target attribute.
    """
    name_lst = name.split('.')
    new_obj = getattr(obj, name_lst[0])
    if len(name_lst) > 1:
        return RecGetattr(new_obj, '.'.join(name_lst[1:]))
    else:
        return new_obj


def RecSetattr(obj, name, value):
    """
    A beefier version of the builtin setattr() that can set sub attributes - attributes of attributes.

    Accomplishes this by recursively calling itself.

    :param obj: Object containing the attribute to be set.
    :param name: Name of the attribute to set including any parent attributes. Should be in the form of: "parent.parent.attribute"
    :param value: Value to set the attribute to
    :return:
    """
    name_lst = name.split('.')
    if len(name_lst) > 1:
        new_obj = getattr(obj, name_lst[0])
        RecSetattr(new_obj, '.'.join(name_lst[1:]), value)
    else:
        setattr(obj, name, value)