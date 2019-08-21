from fissle import c, NamedTuple


@c
class Configuration(NamedTuple):
    a: str = 'A'  # a description
    x: int = 1  # x description


# Hack to enable autocompletion in IDEs
c: Configuration = c


@c
class Cli:
    def subcommand_foo(self):
        """This will be shown in --help for subcommand-foo"""
        print('foo')
        print(c.a)
        print(c.x)

    def subcommand_bar(self):
        """This will be shown in --help for subcommand-bar"""
        print('bar')
        print(repr(c))
