#!/usr/bin/env python3
import click
import pkg_resources
from pathlib import Path


from indico_install.config import ConfigsHolder
from indico_install.utils import options_wrapper
from .setup import aks_setup, ask_for_infra_input
from . import storage, cluster


@click.group("aks")
@click.pass_context
def aks(ctx):
    """
    Indico infrastructure setup and validation for Azure Kubernetes Service
    """
    ctx.ensure_object(dict)


@aks.command("init")
def init():
    values_dir = Path("values")
    if not values_dir.exists():
        values_dir.mkdir(exist_ok=True, parents=True)

    dest_file = values_dir / f"cluster.yaml"
    if dest_file.exists():
        click.secho(
            f"{dest_file.resolve()} already exists. "
            "Please back this file up before running init.",
            fg="red",
        )
        return

    template = pkg_resources.resource_string(__name__, "cluster.yaml")
    with open(dest_file, "wb") as f:
        f.write(template)

    click.secho(f"Created {dest_file}", fg="green")


@aks.command("check")
@click.pass_context
@options_wrapper(check_input=True)
def check(ctx, *, deployment_root, input_yaml, **kwargs):
    """
    Check the state of an existing cluster to validate
    that it meets certain requirements
    """
    aks_setup(deployment_root)
    conf = ConfigsHolder(input_yaml)
    ask_for_infra_input(conf)
    cluster.check(conf)
    storage.check(conf)


@aks.command("create")
@click.pass_context
@click.option(
    "--upload/--no-upload",
    default=False,
    help="Upload Indico API data to the Indico file share",
    show_default=True,
)
@options_wrapper(check_input=True)
def create(ctx, upload=False, *, deployment_root, input_yaml, **kwargs):
    """
    Configure your AKS installation
    """
    aks_setup(deployment_root)
    conf = ConfigsHolder(input_yaml)
    ask_for_infra_input(conf)
    cluster.create(conf)
    storage.create(deployment_root, conf, upload=upload)
