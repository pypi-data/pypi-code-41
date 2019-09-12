#!/usr/bin/env python3
from pathlib import Path
import click
import yaml
from click import secho

from indico_install.infra.eks import cluster, config, database, network, storage
from indico_install.config import ConfigsHolder, merge_dicts
from indico_install.utils import run_cmd, options_wrapper

SOURCES = [network, storage, database, cluster]


@click.group("eks")
@click.pass_context
def eks(ctx):
    """
    Indico infrastructure setup and validation for AWS Kubernetes Service
    """
    ctx.ensure_object(dict)
    if not ((config.access_key and config.access_secret) or config.aws_profile):
        secho("Missing AWS credentials for EKS", fg="yellow")
    else:
        secho(
            f"Using AWS profile: {config.aws_profile}"
            if config.aws_profile
            else f"Using AWS access key: {config.access_key[:5]}****",
            fg="blue",
        )


@eks.command("check")
@click.pass_context
@options_wrapper(check_input=True)
def check(ctx, *, input_yaml, **kwargs):
    """Validate all resources"""
    ctx.obj["SESSION"] = config.Session()
    if not input_yaml.is_file():
        click.secho(f"Could not find {input_yaml}.", fg="red")
        return
    failed = 0
    user_conf = ConfigsHolder(config=input_yaml)
    config.ask_for_infra_input(user_conf)
    user_conf.save()
    for resource in SOURCES:
        resource_name = resource.__name__
        secho(f"Validating {resource_name}...")
        try:
            resource.validate(user_conf, session=ctx.obj["SESSION"])
        except Exception as e:
            secho(f"{resource_name} NOT OK! Error: {e}\n", fg="red")
            failed += 1
        else:
            secho(f"{resource_name} OK!\n", fg="green")
    secho(
        f"Validation complete: {failed} errors",
        fg="red" if failed else "green",
        bold=True,
    )


@eks.command("create")
@click.pass_context
@click.argument("config_file")
@options_wrapper(check_input=True)
def create(ctx, config_file, *, input_yaml, **kwargs):
    """
    Create a new EKS cluster enabled with GPU - uses eksctl in the backend

    Args:

      <CONFIG_FILE> - the name of the config file to use for cluster configuration
    """
    if not Path(config_file).is_file():
        click.secho(f"Config file {config_file} could not be found!", fg="red")

    ctx.obj["SESSION"] = config.Session()
    run_cmd(["eksctl", "create", "cluster", "-f", config_file], tty=True)
    run_cmd(
        "kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v1.12/nvidia-device-plugin.yml"
    )
    user_conf = ConfigsHolder(config=input_yaml)
    with open(config_file, "r") as conf_file:
        conf = yaml.safe_load(conf_file)

    cluster_name = conf["metadata"]["name"]
    nodegroup = conf['nodeGroups'][0]

    if nodegroup.get("privateNetworking", False):
        user_conf["services"] = merge_dicts(
            user_conf.get("services", {}),
            {
                "app-edge": {
                    "values": {
                        "annotations": {
                            "service.beta.kubernetes.io/aws-load-balancer-internal": "0.0.0.0/0"
                        }
                    }
                }
            },
        )
    nodegroup_prefix = (
        f"eksctl-{cluster_name}-nodegroup-{nodegroup['name']}"
    )
    asg = next(
        ctx.obj["SESSION"]
        .ASGClient.get_paginator("describe_auto_scaling_groups")
        .paginate(PaginationConfig={"PageSize": 100})
        .search(f"AutoScalingGroups[?contains(AutoScalingGroupName, `{nodegroup_prefix}`)]"),
        None,
    )
    user_conf["cluster"] = user_conf.get("cluster", {}) or {}
    user_conf["cluster"].update({
        "name": conf["metadata"]["name"],
        "nodegroup_name": asg["AutoScalingGroupName"] if asg else None
    })
    user_conf.save()
