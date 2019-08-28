# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ankisync2']

package_data = \
{'': ['*']}

install_requires = \
['peewee>=3.9,<4.0', 'shortuuid>=0.5.0,<0.6.0']

setup_kwargs = {
    'name': 'ankisync2',
    'version': '0.2.4.1',
    'description': 'Creating and editing *.apkg and *.anki2 safely',
    'long_description': '# AnkiSync 2\n\n[![PyPI version shields.io](https://img.shields.io/pypi/v/ankisync2.svg)](https://pypi.python.org/pypi/ankisync2/)\n[![PyPI license](https://img.shields.io/pypi/l/ankisync2.svg)](https://pypi.python.org/pypi/ankisync2/)\n\n\\*.apkg and \\*.anki2 file structure is very simple, but with some quirks of incompleteness.\n\n[\\*.apkg file structure](https://github.com/ankidroid/Anki-Android/wiki/Database-Structure) is a zip of at least two files.\n\n```\n.\n├── example\n│   ├── example.anki2\n│   ├── media\n│   ├── 1  # Media files with the names masked as integers\n│   ├── 2\n│   ├── 3\n|   └── ...\n└── example.apkg\n```\n\n\\*.anki2 is a SQLite file with foreign key disabled, and the usage of [some JSON schemas](/ankisync2/builder.py) instead of [some tables](/ankisync2/db.py#L46)\n\nAlso, \\*.anki2 is used internally at [`os.path.join(appdirs.user_data_dir(\'Anki2\'), \'User 1\', \'collection.anki2\')`](https://github.com/patarapolw/ankisync/blob/master/ankisync/dir.py#L9), so editing the SQLite there will also edit the database.\n\nThe `media` file is a text file of at least a string of `{}`, which is actually a dictionary of keys -- stringified int; and values -- filenames.\n\n## Usage\n\nSome [extra tables](/ankisync2/db.py#L46) are created if not exists.\n\n```python\nfrom ankisync2.anki import Anki2, Apkg\napkg = Apkg("example.apkg")  # Or Apkg("example/") also works, otherwise the folder named \'example\' will be created.\napkg.db.execute_sql(SQL, PARAMS)\napkg.zip(output="example1.apkg")\n```\n\nI also support adding media.\n\n```python\napkg.add_media("path/to/media.jpg")\n```\n\nTo find the wanted cards and media, iterate though the `Apkg` and `Apkg.iter_media` object.\n\n```python\niter_apkg = iter(apkg)\nfor i in range(5):\n    print(next(iter_apkg))\n```\n\n## Creating a new *.apkg\n\nYou can create a new \\*.apkg via `Apkg` with any custom filename (and \\*.anki2 via `Anki2()`). A folder required to create \\*.apkg needs to be created first.\n\n```python\nfrom ankisync2.anki import Apkg\napkg = Apkg("example")  # Create example folder\n```\n\nAfter that, the Apkg will require at least 1 card, which is connected to at least 1 note, 1 model, 1 template, and 1 deck; which should be created in this order.\n\n1. Model, Deck\n2. Template, Note\n3. Card\n\n```python\nfrom ankisync2 import db\nm = db.Models.create(name="foo", flds=["field1", "field2"])\nd = db.Decks.create(name="bar::baz")\nt = [\n    db.Templates.create(name="fwd", mid=m.id, qfmt="{{field1}}", afmt="{{field2}}"),\n    db.Templates.create(name="bwd", mid=m.id, qfmt="{{field2}}", afmt="{{field1}}")   \n]\nn = db.Notes.create(mid=m.id, flds=["data1", "<img src=\'media.jpg\'>"], tags=["tag1", "tag2"])\nc = [\n    db.Cards.create(nid=n.id, did=d.id, ord=i)\n    for i, _ in enumerate(t)\n]\n```\n\nYou can also add media, which is not related to the SQLite database.\n\n```python\napkg.add_media("path/to/media.jpg")\n```\n\nFinally, finalize with\n\n```python\napkg.zip(output="example1.apkg")\napkg.close()\n```\n\n## Updating an \\*.apkg\n\nThis is also possible, by modifying `db.Notes.data` as `sqlite_ext.JSONField`, with `peewee.signals`.\n\nIt is now as simple as,\n\n```python\nfrom ankisync2.anki import Apkg\nfrom ankisync2 import db\n\napkg = Apkg("example1.apkg")\n\nfor n in db.Notes.filter(db.Notes.data["field1"] == "data1"):\n    n.data["field3"] = "data2"\n    n.save()\n\napkg.close()\n```\n\n## JSON schema of `Col.models`, `Col.decks`, `Col.conf` and `Col.dconf`\n\nI have created `dataclasses` for this at [/ankisync2/builder.py](/ankisync2/builder.py). To serialize it, use `dataclasses.asdict` or\n\n```python\nfrom ankisync2.util import DataclassJSONEncoder\nimport json\njson.dumps(dataclassObject, cls=DataclassJSONEncoder)\n```\n\nFor an example of how this works, please see [/ankisync2/anki.py#L56](/ankisync2/anki.py#L56)\n\n## Using `peewee` framework\n\nYou can also use `peewee` ORM framework; and [ArrayField](/ankisync2/db.py#L21), [X1fField](/ankisync2/db.py#L31) and [JSONField](/ankisync2/db.py#L31) will be automated. You can use Dataclasses and Lists directly, without converting them to string first.\n\n## Examples\n\nPlease see [/example.ipynb](/example.ipynb).\n\n## Installation\n\n```bash\npip install ankisync2\n```\n\n# Related projects\n\n- <https://github.com/patarapolw/ankisync>\n- <https://github.com/patarapolw/AnkiTools>\n',
    'author': 'Pacharapol Withayasakpunt',
    'author_email': 'patarapolw@gmail.com',
    'url': 'https://github.com/patarapolw/ankisync2',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
