# Проверка парсера

# Парсинг документа

# Разделение на блоки

# Разделение на параграфы

# Общий запуск
from formatter.parser import Parser
from formatter.source import BaseSource

def test_work():
    tree = Parser().load(BaseSource.init(url='https://github.com/python/peps.git'))
    pass