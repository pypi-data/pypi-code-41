# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['umwelt', 'umwelt.decoders']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=0.17,<1']

setup_kwargs = {
    'name': 'umwelt',
    'version': '2019.8.1',
    'description': 'Configure your program via environment variables, validated by pydantic.',
    'long_description': '# Umwelt\n\n[dataclasses]: https://docs.python.org/3/library/dataclasses.html\n[pydantic]: https://pydantic-docs.helpmanual.io/\n\nDescribe a configuration schema with [dataclasses][] or [pydantic][] and\nload values from the environment, in a static-typing-friendly way.\n\n```python\n>>> os.environ["APP_DB_PORT"] = "32"\n```\n\n```python\nimport umwelt\nfrom typing import Tuple\nfrom pydantic import UrlStr\n\n@umwelt.subconfig  # only needed on nested configs\nclass DbConfig:\n    port: int\n\nclass MyConfig:\n    db: DbConfig  # nested\n    hosts: Tuple[UrlStr, ...] = ("http://b.org", "http://sky.net")  # default value\n\nconfig = umwelt.new(MyConfig, prefix="app")\n```\n\n```python\n>>> is_dataclass(config)\nTrue\n>>> config.hosts\n("http://b.org", "http://sky.net")\n>>> config.db.port\n32\n```\n\n## Install\n\n```shell script\n$ pip install umwelt\n```\n\n## Features\n\n### umwelt.new\n\n`umwelt.new` expects one positional argument: the config class to fill.\nUmwelt will convert it into a [dataclass][dataclasses] if it\'s not one already.\n\n`umwelt.new` also accepts named arguments:\n- **`source`** (by default `os.environ`) is a `Mapping[str, str]` from which\nvalues are extracted.\n- **`prefix`** can be a string or a callable. As a string, it is prepended to\nthe config field\'s name. As a callable, it receives the config field\'s name and\nits result is the source key name.\n- **`decoder`** is a callable expecting a type and a string, and returns a\nconversion of that string in that type, or in a type that pydantic can convert\nin that type.\nFor example, when umwelt\'s default `decoder` is called with (`List[Set[int]]`,\n`"[[1]]"`), it simply decodes the string from JSON and hence returns a list of\n_lists_, which pydantic properly converts into a list of _sets_. \n\n### @umwelt.subconfig\n\n`@umwelt.subconfig` tags classes so that, when they appear as field annotations\nin another config class, `umwelt.new` doesn\'t instantiate them from a single\n`source` value, but rather from one `source` value _per class field_.\n\nExample:\n\n```python\nclass Point:                              # no @subconfig\n    def __init__(self, s: str):           # string input\n        self.x, self.y = s.split(",", 1)  # arbitrary implementation\n\nclass MyConf:\n    point: Point\n\nconf = umwelt.new(MyConf, source={"POINT": "1,2"})  # one source entry\nconf.point  # <Point at 0x7f07b1d04750>\n```\n\n`conf.point` is an instance of _Point_, built by passing the input value `"1,2"`\ndirectly to `Point.__new__`.\nThere is only one `source` key: `POINT`.\n\nNow compare with `@umwelt.subconfig`:\n\n```python\n@umwelt.subconfig\nclass Point:\n    x: int\n    y: int\n\nclass MyConf:\n    point: Point\n\nconf = umwelt.new(MyConf, source={"POINT_X": "1", "POINT_Y": "2"})\nconf.point  # Point(x=1, y=2)\n```\n\n`conf.point` is still an instance of _Point_ (_Point_ has been made a\ndataclass by Umwelt, hence the automatic `__str__` implementation).\nThere are **two** `source` keys: `POINT_X` and `POINT_Y`, each corresponding to\na field of the _Point_ class.\n\n## Comparison with Ecological\n\nI\'ve used [Ecological][] for a long time.\nToday, a large part of Ecological\'s codebase implements features already found\nin [dataclasses][] and [pydantic][], which are more mature.\nI believe Ecological\'s design can be dramatically simplified _and_ improved by\nenforcing a strict separation of concerns:\n\n- class scaffolding is the responsibility of [dataclasses][] (which, compared\n  to metaclasses, is simpler, more introspectable, and comes with helpers like\n  `asdict`);\n- type coercion and validation is the responsibility of [pydantic][] (which has\n  more features, e.g. nested data types, JSON Schema, serialization, etc.);\n- mapping a [pydantic][] schema (the configuration class) to a string-to-string\n  dict (like `os.environ`) is the responsibility of Umwelt.\n\nSome compatibility-breaking decisions prevent from doing this in Ecological:\n\n- Don\'t autoload configuration values, especially not at class definition time.\n  Instead, offer just one function (`umwelt.new`) that loads the configuration\n  when it is called.\n- Don\'t tie variable prefixes to configuration classes, as that doesn\'t play\n  well with nested configurations.\n\n[ecological]: https://github.com/jmcs/ecological\n[autoloading]: https://github.com/jmcs/ecological/issues/20\n',
    'author': 'Thibaut Le Page',
    'author_email': 'thilp@thilp.net',
    'url': 'https://github.com/thilp/umwelt',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
