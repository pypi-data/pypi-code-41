#!/usr/bin/env python
"""Spell check reStructuredText."""

import os
import sys
from glob import glob

import click
from docutils.parsers.rst import Parser, Directive, directives, roles
from docutils.utils import new_document
from docutils.frontend import OptionParser
from docutils.nodes import Text
import spacy


__version__ = '0.1.0'


class IgnoredDirective(Directive):
    """Stub for unknown directives."""

    has_content = True

    def run(self):
        """Do nothing."""
        return []


def ignore_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    """Stub for unknown roles."""
    # pylint: disable=unused-argument
    return ([], [])


# ignore Sphinx directives
ignored = ['todo', 'toctree', 'autoclass', 'graphviz', 'automodule']
for ignore in ignored:
    directives.register_directive(ignore, IgnoredDirective)

iroles = ['py:class', 'ref']
for role in iroles:
    roles.register_local_role(role, ignore_role)


TEXT_NODES = set(['block_quote', 'paragraph', 'list_item', 'term', 'definition_list_item', 'title'])


def is_misspelled(token):
    if token.like_url or token.like_num or token.like_email:
        return False
    return token.is_oov


@click.command()
@click.argument('files', nargs=-1)
@click.option(
    '-d',
    '--dictionary',
    help='spaCy language model (spacy.io/models), e.g. en_core_web_md',
    default='en_core_web_md',
)
def main(files, dictionary):
    """Spell check reStructuredText."""
    parser = Parser()
    settings = OptionParser(components=(Parser,)).get_default_values()
    nlp = spacy.load(dictionary)
    any_misspellings = False
    for file in files:
        for filename in glob(file):
            document = new_document(filename, settings)
            p = parser.parse(open(filename, 'r').read(), document)
            misspellings = set()
            for node in parser.document.traverse(Text):
                if (
                    node.tagname == '#text'
                    and node.parent
                    and node.parent.tagname in TEXT_NODES
                    and (
                        (node.parent.parent and node.parent.parent.tagname != 'system_message')
                        or not node.parent.parent
                    )
                ):
                    misspellings |= set(
                        token.text for token in nlp(node.astext()) if is_misspelled(token)
                    )

            if misspellings:
                any_misspellings = True
                print(f'✘ {filename}')
                print(*misspellings, sep='\n')
            else:
                print(f'✔ {filename}')
    sys.exit(os.EX_DATAERR if any_misspellings else os.EX_OK)


if __name__ == '__main__':
    main()
