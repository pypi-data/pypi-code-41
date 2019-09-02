# Тестирование работы дерева
import pytest

from formatter import Document, Root, Paragraph, Line, Block
from formatter.tree import BaseTree

# Добавление ребенка
from tests.parametrize_set import NODES_LIST


def test_normal_create_child(root):
    document = root.create_child()
    assert root.to_dict() == {'content': None, 'type': 'Root', 'filename': None, 'path': None, 'children': [
        {'content': None, 'type': 'Document', 'filename': None, 'path': None, 'children': []}]}
    block = document.create_child()
    assert root.to_dict() == {'path': None, 'type': 'Root', 'content': None, 'filename': None, 'children': [
        {'path': None, 'type': 'Document', 'content': None, 'filename': None,
         'children': [{'path': None, 'type': 'Paragraph', 'content': None, 'filename': None, 'children': []}]}]}
    block.create_child()
    assert root.to_dict() == {'type': 'Root', 'path': None, 'filename': None, 'content': None, 'children': [
        {'type': 'Document', 'path': None, 'filename': None, 'content': None, 'children': [
            {'type': 'Paragraph', 'path': None, 'filename': None, 'content': None,
             'children': [{'type': 'Block', 'path': None, 'filename': None, 'content': None, 'children': []}]}]}]}


@pytest.mark.parametrize('node', NODES_LIST)
def test_create_child_with_custom_type(node):
    parents = [Root, Document, Block, Line, Paragraph]
    for _parent in parents:
        parent = _parent()
        _child = parent.create_child(child_type=node)
        assert isinstance(parent.children[0], node)
        assert isinstance(_child, node)
        assert _child is parent.children[0]


@pytest.mark.parametrize('node', NODES_LIST)
def test_append_child(node):
    parents = [Root, Document, Block, Line, Paragraph]
    for _parent in parents:
        parent = _parent()
        parent._append(node(position=777))
        assert isinstance(parent.children[0], node)
        assert parent.children[0].position == 777


# Получение следующего элемента в дереве
def test_next_child(block):
    _block = block()
    line1 = _block.create_child()
    line2 = _block.create_child()
    assert line1.position == 0
    assert line1.next().position == 1
    assert line2.next() is None
    _block.create_child()
    assert line2.next().position == 2

    assert line2.position == 1
    assert line2.previous().position == 0
    assert line1.previous() is None


# Преобразование в JSON
def test_to_dict(base_tree):
    """Базовая конвертация"""
    BaseTree.from_dict(base_tree.to_dict())


def test_tree_length(small_tree):
    assert len(small_tree) == 5
