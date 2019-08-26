# --- Standard Library Imports ------------------------------------------------
# None

# --- Third Party Imports -----------------------------------------------------
import click

# --- Intra-Package Imports ---------------------------------------------------
from rtm.main import api


@click.command()
def main():
    api.main()
