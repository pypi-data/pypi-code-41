from bs4 import BeautifulSoup
from slugify import slugify


class FileNode:
    KIND_DIRECTORY = 'dir'
    KIND_FILE = 'file'

    def __init__(self, name, kind):
        self.children = []
        self.parent = None
        self.kind = kind
        self.name = name

    def __str__(self):
        return '{} {} {}'.format(self.name, self.kind, self.children) 

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def get_ancestors(self):
        ancestors = []
        file_node = self
        while file_node.parent is not None:
            ancestors.insert(0, file_node)
            file_node = file_node.parent
        return ancestors

    def get_url(self):
        return '/{}.html'.format(self.get_path())

    def get_path(self):
        names = [ slugify(file_path.name) for file_path in self.get_ancestors() ]
        return '/'.join(names)

    def get_html(self):
        raise NotImplementedError('Method .get_html() is not implemented')

    def get_edit_url(self):
        raise NotImplementedError('Method .get_edit_url() is not implemented')

    def get_text(self):
        html = self.get_html()
        soup = BeautifulSoup(html, 'html.parser')
        return soup.getText() 