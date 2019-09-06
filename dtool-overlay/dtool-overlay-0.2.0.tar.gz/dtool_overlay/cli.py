"""dtool_config.cli module."""

import dtoolcore
import click

from dtool_cli.cli import dataset_uri_argument

from dtool_overlay.utils import (
    TransformOverlays,
    bool_overlay_from_glob_rule,
    pair_overlay_from_suffix,
    value_overlays_from_parsing,
)


@click.group()
def overlays():
    """Overlays provide per item structural metadata."""


@overlays.command()
@dataset_uri_argument
def show(dataset_uri):
    """Show the overlays as CSV table."""
    ds = dtoolcore.DataSet.from_uri(dataset_uri)
    overlays = TransformOverlays.from_dataset(ds)
    click.secho(overlays.to_csv())


@overlays.group()
def template():
    """Create overlay CSV template.

    Templates can be saved as overlays using the ``dtool overlays write``
    command.
    """


@template.command()
@dataset_uri_argument
@click.argument("overlay_name")
@click.argument("glob_rule")
def glob(dataset_uri, overlay_name, glob_rule):
    """Create template with boolean values based on matching of a glob rule.

    For example, one could create an overlay named "is_csv" using the glob_rule
    "*.csv".

    dtool overlays template glob <DS_URI> is_csv '*.csv'

    Note that the glob_rule needs to be quoted on the command line to avoid the
    shell expanding it.
    """
    ds = dtoolcore.DataSet.from_uri(dataset_uri)
    overlays = bool_overlay_from_glob_rule(overlay_name, ds, glob_rule)
    click.secho(overlays.to_csv())


@template.command()
@dataset_uri_argument
@click.argument("parse_rule")
def parse(dataset_uri, parse_rule):
    """Create template by parsing relpaths.

    For example, consider the relpath structure "repl_1/salt/result.csv"
    one could create overlays named "replicate", "treatment" using
    the command below.

    dtool overlays template parse <DS_URI>  \\
      'repl_{replicate:d}/{treatment}/result.csv'

    The parse_rule needs to be quoted on the command line to avoid the shell
    expanding it.

    Note that the replicate values will be typed as integers, see
    https://pypi.org/project/parse/ for more details.

    It is possible to ignore parts of a relpath by using a pair of curly
    braces without a name in it. The command below is different from that
    above in that it only creates a "replicate" overlay.

    dtool overlays template parse <DS_URI>  \\
      'repl_{replicate:d}/{}/result.csv'

    """
    ds = dtoolcore.DataSet.from_uri(dataset_uri)
    overlays = value_overlays_from_parsing(ds, parse_rule)
    click.secho(overlays.to_csv())


@template.command()
@dataset_uri_argument
@click.option("-n", "--overlay_name")
@click.argument("suffix")
def pairs(dataset_uri, overlay_name, suffix):
    """Create template with pair item identifiers for files with common prefix.

    For example, consider the relpaths:

    exp1/read1.fq.gz
    exp1/read2.fq.gz
    exp2/read1/fq.gz
    exp2/read2/fq.gz

    One could create an overlay named "pair_id"  for these using the command

    dtool overlays template pairs <DS_URI> .fq.gz

    The suffix above (.fq.gz) results in the common prefixes would be
    "exp1/read" and "exp2/read". This is then used to find matching pairs.
    """
    if overlay_name is None:
        overlay_name = "pair_id"
    ds = dtoolcore.DataSet.from_uri(dataset_uri)
    overlays = pair_overlay_from_suffix(overlay_name, ds, suffix)
    click.secho(overlays.to_csv())


@overlays.command()
@dataset_uri_argument
@click.argument('csv_template', type=click.File('r'))
def write(dataset_uri, csv_template):
    """Add overlays from CSV template to dataset.

    For example to add an overlay stored in the file "template.csv":

    dtool overlays write <DS_URI> template.csv

    To stream content from stdin use "-", e.g.

    dtool overlays glob <URI> is_csv '*.csv' | dtool overlays write <URI> -
    """
    ds = dtoolcore.DataSet.from_uri(dataset_uri)
    csv_content = csv_template.read()
    overlays = TransformOverlays.from_csv(csv_content)
    overlays.put_in_dataset(ds)
