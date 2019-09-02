from formatter.tree.nodes import Root, Block, Line, Document, Paragraph

GIT_URLS = (
    ('https://github.com/python/peps.git', True),
    ('git@github.com:python/peps.git', True),
    ('git@gitlab.com:k0d/k0d/general-page.git', True),
    ('https://gitlab.com/k0d/k0d/general-page.git', True),
    ('https://yandex.ru', False)
)

URLS_SET = (
    ('https://gitlab.com/k0d/k0d/general-page.git', True),
    ('https://yandex.ru', True),
    ('https://github.com/python/peps.git', True),
    ('/', False),
    ('sdfsdf', False)
)

NODES_LIST = (Document, Block, Paragraph, Line)
