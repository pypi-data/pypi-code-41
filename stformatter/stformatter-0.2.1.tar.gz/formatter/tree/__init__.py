import collections
import json
import uuid

from formatter.tree.serializer import BaseNodeDBSerializator


class BaseTree:
    """
    Базовый класс нод.
    Управляет связями между нодами, добавлением элементов, преобразованием, и вообще всем.
    """
    def __init__(self, *args, position=0, **kwargs):
        self.type = self.__class__.__name__
        self.position = position # Позиция в списке children у родителя
        self.children = [] # Список детей
        self.parent = None # Ссылка на родителя
        self.children_type = None # Стандартный тип детей
        self._previous = None # Ссылка на предидущий объект у родителя
        self._next = None # Ссылка на следующий объект родителя
        self.content = None
        self.filename = None
        self.path = None

    def __str__(self):
        return self.content or ''

    def __len__(self):
        return sum(map(len, self.children)) + 1

    def get_parent(self, parent_type=None):
        """Найти родителя заданного типа"""
        if parent_type and self.type == parent_type:
            return self

        if self.parent:
            return self.parent.get_parent(parent_type)

    def create_child(self, *args, child_type=None, **kwargs):
        """Создать ребенка"""
        kwargs['position'] = len(self.children)
        if child_type:
            _child = child_type(*args, **kwargs)
        else:
            _child = self.children_type(*args, **kwargs)
        self._append(_child)
        return _child

    def _append(self, node):
        """Добавить ноду в этот корень"""
        self._next = None
        self._previous = None
        node.parent = self
        self.children.append(node)

    def previous(self):
        """Предидущий объект того же типа"""
        if self.position == 0:
            return None
        if not self._previous:
            self._previous = self.parent.children[self.position - 1]

        return self._previous

    def next(self):
        """Следующий объект того же типа"""
        if self.parent.children[-1].position == self.position:
            return None
        if not self._next:
            self._next = self.parent.children[self.position+1]

        return self._next

    def to_dict(self):
        _object = BaseNodeDBSerializator().dump(self)
        _object['children'] = []
        if self.children:
            list(map(lambda _child:_object['children'].append(_child.to_dict()), self.children))

        return _object

    @classmethod
    def from_dict(cls, source):
        _children = source.pop('children')

        _object = BaseNodeDBSerializator().load(source)

        node_class = list(filter(lambda x: x.__name__ == _object.get('type'), BaseTree.__subclasses__()))
        node_class = node_class[0] if node_class else None
        object = node_class(**_object)

        for _child in _children:
            object._append(cls.from_dict(_child))

        return object
