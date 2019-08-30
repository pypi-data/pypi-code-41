"""
Main module for demotype command-line utility.
"""

from demotype.demo import Doc
from pynput.keyboard import Listener, Key
import click

global doc
doc = None

def on_release(key):
    global doc
    if key == Key.f3:
        doc.print_next()

@click.command()
@click.argument('filename', type=click.Path(exists=True))
def cli(filename):
    global doc
    with open(filename, 'r') as f:
        doc = Doc(f.read())
    l = Listener(on_release = on_release)
    l.start()
    l.join()

