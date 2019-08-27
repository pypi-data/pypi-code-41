import click
import json


def target_print_json(metrics, **kwargs):
    metrics_json = json.dumps(metrics, indent=4)
    click.echo(metrics_json)
