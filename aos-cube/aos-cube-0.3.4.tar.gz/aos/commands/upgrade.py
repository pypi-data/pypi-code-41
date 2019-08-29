import click
from aos.util import popen

# Upgrade command
@click.command(
    "upgrade", short_help="Upgrade aos-cube to latest")
def cli():
    """ Run pip upgrade process to keep aos-cube up-to-date. """
    cmd = ["pip", "install", "--upgrade", "aos-cube"]
    try:
        ret = popen(cmd)
        if ret != 0:
            cmd.insert(3, "--no-cache-dir")
            popen(cmd)
    except Exception as e:
        raise e
