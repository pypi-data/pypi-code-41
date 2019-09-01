from formatter.tree.nodes import Root


class Parser:
    """Деление документа на параграфы и блоки"""
    STATUS = ('idle', 'parsing', 'raw', 'formatting', 'done')
    def __init__(self):
        """Принимает на вход объект Source и из него формирует Document"""
        self.root = Root()
        self.status = None

        self.document = None
        self.paragraph = None
        self.block = None
        self.line = None

        self.prev_line = []  # Ссылка на 2 предидущих объекта
        self.position = 0
        self.line_number = 1

    def get_status(self):
        if self.status is None:
            return
        return self.STATUS[self.status]

    def close_element(self):
        if self.block:
            self.block = None
            return
        if self.paragraph:
            self.paragraph = None
            return

    def append_element(self, index, content):
        if not self.paragraph:
            self.paragraph = self.document.create_child()

        if not self.block:
            self.block = self.paragraph.create_child()

        self.block.create_child(line_number=index, content=content)

    def read_document(self, file):
        try:
            for index, line in enumerate(file.readlines()):
                _content = line.strip('\n')
                if not _content:
                    self.close_element()
                else:
                    self.append_element(index, _content)

        except UnicodeDecodeError:
            print(f'Ошибка при чтении файла {self.document.path}')
            return

        return self.document

    def load(self, source):
        """Формирование дерева"""
        with source as _source:
            for _file in _source.files:
                self.document = self.root.create_child()
                self.read_document(_file)
        return self.root

    def parsing(self, formatter):
        """Применение правил формата"""
        pass
