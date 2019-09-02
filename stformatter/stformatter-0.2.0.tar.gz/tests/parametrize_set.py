from formatter.tree.nodes import Root, Block, Line

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

TEST_TREE = Root()
document = TEST_TREE.create_child()
block = document.create_child(child_type=Block, content='Block')
block.create_child(child_type=Line, content='Line', line_number=1)
block.create_child(child_type=Line, content='Line2', line_number=2)
