from tree.nodes import Root, Block, Line

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

TEST_TREE_JSON = """{"path": null, "type": "Root", "position": 0, "children": [{"path": null, "type": "Document", "position": 0, "children": [{"path": null, "type": "Block", "position": 0, "children": [{"path": null, "type": "Line", "position": 0, "children": [], "line_number": 1, "filename": null, "id": "f3a1ad16-ccad-11e9-bdad-a8667f3458c4", "content": "Line"}, {"path": null, "type": "Line", "position": 1, "children": [], "line_number": 2, "filename": null, "id": "f3a1ae38-ccad-11e9-bdad-a8667f3458c4", "content": "Line2"}], "filename": null, "id": "f3a1abd6-ccad-11e9-bdad-a8667f3458c4", "content": null}], "filename": null, "id": "f3a1aa5a-ccad-11e9-bdad-a8667f3458c4", "content": null}], "filename": null, "id": "f3a1a71c-ccad-11e9-bdad-a8667f3458c4", "content": null}"""