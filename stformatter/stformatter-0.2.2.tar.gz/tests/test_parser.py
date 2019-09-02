# Проверка парсера

# Парсинг документа

# Разделение на блоки

# Разделение на параграфы

# Общий запуск
from formatter import BaseTree
from formatter.parser import Parser
from formatter.source import BaseSource

def test_base_work():
    _source = BaseSource.init(url='https://github.com/python/peps.git')
    _tree = Parser().load(_source)
    _to_dict = _tree.to_dict()
    _from_dict = BaseTree.from_dict(_to_dict)
