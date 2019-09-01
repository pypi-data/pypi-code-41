import json
import uuid

from formatter.tree.serializer import BaseNodeDBSerializator


class BaseTree:
    """
    Базовый класс нод.
    Управляет связями между нодами, добавлением элементов, преобразованием, и вообще всем.
    """
    def __init__(self, *args, position=0, **kwargs):
        self.id =  kwargs.get('id', uuid.uuid1()) # Ключ
        self.type = self.__class__.__name__
        self.db = None # Объект общения с базой
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
        node.parent = self
        self.children.append(node)

    @property
    def previous(self):
        """Предидущий объект того же типа"""
        if not self._previous and self.parent.children[-1] != self.position:
            self._previous = self.parent.children[self.position-1]
        return self._previous

    @property
    def next(self):
        """Следующий объект того же типа"""
        if not self._next and self.position != 0:
            self._next = self.parent.children[self.position - 1]
        return self._next

    def to_json(self):
        return json.dumps(BaseNodeDBSerializator().dump(self))
