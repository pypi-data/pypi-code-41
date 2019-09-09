"""
Jacob Thompson

misc
"""
import numpy as np
from matplotlib import pyplot as plot
from skimage.transform import resize
import time

class Timer:
    def __init__(self):
        self.tictoc = time.time()

    def tic(self):
        self.tictoc = time.time()

    def toc(self):
        return time.time() - self.tictoc


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


class TimeList:
    def __init__(self, list_in=None):
        """
        This is a simple wrapper class for a list that will also keep track of the time when an element was added to the
        list.

        This class has three primary attributes:
            TimeList.list: The actual values of the list.
            TimeList.time: The time that each value was added to the list.
            TimeList.rel_time: The time that each value was added to the list since the list was created.

        :param list_in: Initial iterable to populate the list
        """
        self.start_time = time.time()
        if list_in:
            self.list = list(list_in)
            self.time = [self.start_time] * len(self.list)
            self.rel_time = [0.] * len(self.list)
        else:
            self.list = []
            self.time = []
            self.rel_time = []

    def append(self, item):
        """
        Appends an item to the list and keeps track of the time that it was added.

        :param item: Item to append to the list
        :return:
        """
        current = time.time()
        self.time.append(current)
        self.rel_time.append(current - self.start_time)
        self.list.append(item)


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