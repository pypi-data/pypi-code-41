# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['pytest_notimplemented']
install_requires = \
['pytest>=5.1,<6.0']

entry_points = \
{'pytest11': ['notimplemented = pytest_notimplemented']}

setup_kwargs = {
    'name': 'pytest-notimplemented',
    'version': '1.0.0',
    'description': 'Pytest markers for not implemented features and tests.',
    'long_description': 'pytest-notimplemented\n=====================\nA pytest plugin providing a marker for not implemented features and tests.\n\n@mark.notimplemented\n--------------------\n\nThe `notimplemented` marker is designed to be used for tests which should fail because\nthe feature is not yet implemented.\n\nAs tests on not implemented features should fail, it is just syntatic sugar for a\nstandard `xfail` marker with a "Not implemented" message.\n\n```python\n    from pytest import mark\n\n    @mark.notimplemented\n    def test_foo(foo):\n        assert foo.baz()\n\n    @mark.xfail("Not implemented")\n    def test_bar(bar):\n        assert bar.baz()\n```\n\n@mark.notwritten\n-----------------\n\nThe `notwritten` marker is is designed to be used for tests which are declared but not\ndefined. Those kind of tests are just placeholders to help the developer remember that\nthe behavior must be tested. And that marker helps on it.\n\nAs not written tests (or tests not finished to write) are impredictable, they must be\nskipped. That marker is just syntatic sugar for a standard `skip` marker with a\n"Not written" message.\n\n```python\n    from pytest import mark\n\n    @mark.notwritten\n    def test_foo(foo):\n        pass\n\n    @mark.skip("Not written")\n    def test_bar(bar):\n        pass\n```',
    'author': 'Damien Flament',
    'author_email': 'damien.flament@gmx.com',
    'url': 'https://github.com/neimad/pytest-notimplemented',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
