# pylint: disable=E0213

import sys

__all__ = ['Todo', 'VERSION']

VERSION = '0.1.1'


class Classproperty:
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class Todo:
    items = []
    completed = []

    @classmethod
    def add(cls, task):
        cls.items.append(task)
        return (True, f'{task} is added .\n')

    @Classproperty
    def list_todos(cls):
        for index, task in enumerate(cls.items, 1):
            sys.stdout.write('{0:04d} : {1}\n'.format(index, task))

    @classmethod
    def complete(cls, index):
        index = index - 1
        removed_task = cls.items.pop(index)
        cls.completed.append(removed_task)
        return (True, f'{removed_task} is completed!\n')

    @Classproperty
    def completed_list(cls):
        for index, task in enumerate(cls.completed, 1):
            sys.stdout.write('{0:04d} : {1}\n'.format(index, task))
