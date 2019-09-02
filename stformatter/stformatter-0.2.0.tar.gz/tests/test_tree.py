# Тестирование работы дерева
import json

from formatter.tree import BaseNodeDBSerializator, BaseTree
from tests.parametrize_set import TEST_TREE


# Добавление ребенка

# Получение следующего элемента в дереве

# Преобразование в JSON
def test_to_json():
    # from tree
    _json = TEST_TREE.to_dict()
    # to tree
    tree = BaseTree.from_dict(_json)
    pass
