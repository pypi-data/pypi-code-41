import pytest
from rftoc import rftoc


@pytest.mark.parametrize(
    'arg',
    [
        ('name: someslide\n# Foo'.split('\n'), '* [Foo](#someslide)\n'),
        ('name: someslide\n# Foo-Bar'.split('\n'), '* [Foo-Bar](#someslide)\n'),
        ('name: someslide\n# Foo-Bar `Baz`'.split('\n'), '* [Foo-Bar `Baz`](#someslide)\n'),
        ('name: someslide\n## Foo'.split('\n'), '    + [Foo](#someslide)\n'),
        ('name: someslide\n### Foo'.split('\n'), '        - [Foo](#someslide)\n'),
        ('name: someslide\n#### Foo'.split('\n'), '            * [Foo](#someslide)\n'),
        (

'''
name: first
# foo

name: second
## bar
'''.split('\n')
,

'''\
* [foo](#first)
    + [bar](#second)
'''
        ),
    ],
)
def test_foo(arg):
    src, expected = arg

    toc = rftoc(src)
    assert toc == expected


@pytest.mark.parametrize(
    'arg',
    [
        ('name: someslide\n### Foo'.split('\n'), '        - [Foo](#someslide)\n'),
        ('name: someslide\n#### Foo'.split('\n'), ''),
    ]
)
def test_bar(arg):
    src, expected = arg

    toc = rftoc(src, max_level=3)
    assert toc == expected
