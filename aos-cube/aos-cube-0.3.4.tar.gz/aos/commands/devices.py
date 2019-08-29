import sys
import json
import click

from serial.tools.list_ports import comports

# Make command
@click.command("devices", short_help="List devices on serial ports")
def cli():
    """ List devices on serial ports """
    arr = []
    for p in comports():
        j = json.dumps(p.__dict__)
        arr.append(json.loads(j))
    print(json.dumps(arr, indent = 4))
    sys.exit(0)
