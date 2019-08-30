import sys
from io import StringIO
from unittest.mock import patch

from ocdsextensionregistry.cli.__main__ import main

args = ['ocdsextensionregistry']


def test_command(monkeypatch, tmpdir):
    with patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', args)
        main()

    assert 'usage: ocdsextensionregistry' in actual.getvalue()
