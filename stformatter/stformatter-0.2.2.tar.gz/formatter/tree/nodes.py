import os

from formatter.tree import BaseTree


class Root(BaseTree):
    def __init__(self, *args, **kwargs):
        super(Root, self).__init__(*args, **kwargs)
        self.children_type = Document


class Document(BaseTree):
    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        self.children_type = Paragraph
        _file = kwargs.get('file')
        self.file = open(_file) if _file else None
        self.path, self.filename = os.path.split(kwargs.get('file')) if _file else (
        kwargs.get('path'), kwargs.get('filename'))

    def __str__(self):
        return self.filename


class Paragraph(BaseTree):
    """Разделение по 2 пустые строки"""
    def __init__(self, *args, **kwargs):
        super(Paragraph, self).__init__(*args, **kwargs)
        self.children_type = Block


class Block(BaseTree):
    """Разделение пустой строкой"""
    def __init__(self, *args, **kwargs):
        super(Block, self).__init__(*args, **kwargs)
        self.children_type = Line


class Line(BaseTree):
    def __init__(self, *args, **kwargs):
        super(Line, self).__init__(*args, **kwargs)
        self.content = kwargs.get('content', None)  # Готовое значение
        self.line_number = kwargs.get('line_number', None)

    def __bool__(self):
        return bool(self.content)


class Sentence(BaseTree):
    def __init__(self, *args, **kwargs):
        super(Sentence, self).__init__(*args, **kwargs)


# Базовые элементы форматированного дерева

class Text(Block):
    """Текстовый блок"""


class Code(Block):
    """Блок с кодом"""


class EmbedBlock(Block):
    """Embed элемент с интерактивом"""


class Table(Block):
    """Таблица"""


class List(Block):
    """Список"""


class Image(BaseTree):
    """Хранение изображения"""


class Link(BaseTree):
    """Хранение ссылки"""


# Атомарные объекты дерева
# Эти элементы должны храниться в content

class Term(BaseTree):
    """Слово"""


class Phraze(BaseTree):
    """Не делимые выражения"""
