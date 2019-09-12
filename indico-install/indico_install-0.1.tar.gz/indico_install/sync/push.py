import re

import click
from click import confirm, secho

from indico_install.config import ConfigsHolder
from indico_install.helm.apply import apply
from indico_install.helm.render import render
from indico_install.kube.svc import restart
from indico_install.utils import run_cmd, options_wrapper

from indico_install.sync.utils import APP_MAP, get_app_hashes, get_non_matching_images

REVERSE_APP_MAP = {value: key for key, value in APP_MAP.items()}


@click.group("push")
@click.pass_context
def push(ctx):
    """Push hash(es) and image(s) to the cluster"""
    ctx.ensure_object(dict)


@push.command("all")
@click.pass_context
@options_wrapper(check_services=True, check_input=True)
def push_all(
    ctx, *, input_yaml, services_yaml, cluster, yes, deployment_root, forwarded=True
):
    """
    All service and frontend hashes in the services yaml
    will be pushed to the current cluster.
    """
    if forwarded is True:
        ctx.invoke(push_all, forwarded=False)

    configs = ConfigsHolder(config=services_yaml)
    for (
        _,
        resource,
        deployment,
        saved_image,
        cluster_image,
    ) in get_non_matching_images(configs):
        secho(f"{deployment}:\nOn Cluster: {cluster_image}\nOn Disk: {saved_image}")

        if yes or confirm("Push new image?"):
            secho(
                run_cmd(
                    f"kubectl set image --record=true {resource}/{deployment} "
                    f"{deployment}=gcr.io/new-indico/{saved_image}"
                ),
                fg="green",
            )
        else:
            secho(f"Skipping {deployment}", fg="yellow")

    # Frontend
    ctx.invoke(
        render,
        service="app-edge-nginx-conf",
        deployment_root=deployment_root,
        cluster=cluster,
        input_yaml=input_yaml,
        services_yaml=services_yaml,
    )
    ctx.invoke(
        apply, service="app-edge-nginx-conf", deployment_root=deployment_root, yes=yes
    )
    ctx.invoke(restart, service="app-edge")
    secho("Done pushing changes", fg="green")


@push.command("image")
@click.pass_context
@click.argument("image_name")
@click.argument("image", required=False, default=None)
@options_wrapper(check_services=True)
def push_image(ctx, image_name, *, services_yaml, yes, image=None, **kwargs):
    """
    Update <IMAGE_NAME> matching deployment/statefulset
    with image saved in current cluster config.
    Ex. indico push image noct
    """
    resources = []
    for resource_type, column in [("deployment", 7), ("statefulset", 5)]:
        options = run_cmd(
            f"kubectl get {resource_type} -o wide "
            f"| grep indico "
            f"| awk '${column} ~ /{image_name}/ {{print $1}}'",
            silent=False,
        )

        resources.extend(
            [(resource_type, resource) for resource in options.split("\n") if resource]
        )

    if image is None:
        configs = ConfigsHolder(config=services_yaml)
        image = configs["images"][image_name.replace("-", "").replace("_", "")]

    for resource_type, resource in resources:
        secho(f"{resource_type}/{resource}:\n Update with: {image}")

        if yes or confirm("Push new image?"):
            secho(
                run_cmd(
                    "kubectl set image --record=true "
                    f"{resource_type}/{resource} {resource}=gcr.io/new-indico/{image}",
                    silent=True,
                )
            )
        else:
            secho(f"Skipping {resource}", fg="yellow")


@push.command("client")
@click.pass_context
@click.argument("client")
@click.argument("hash")
def push_client(ctx, client, hash):
    """Update frontend <CLIENT> with <HASH>. Will also update app_edge"""
    app_hashes = get_app_hashes()
    if client in REVERSE_APP_MAP:
        client = REVERSE_APP_MAP[client]
    elif client not in APP_MAP:
        secho(f"provided client must be one of {APP_MAP.keys()} or {APP_MAP.values()}")

    current_hash = app_hashes[APP_MAP[client]]
    output = run_cmd(
        """kubectl get configmap app-edge-nginx-conf -o json | jq '.data["nginx.conf"]'""",
        silent=True,
    )

    secho(rf"Looking for {client}([^;]+){current_hash}")
    secho(rf"Replacing with {client}   \1{hash}")

    # \1 capturing group doesn't work
    match = re.findall(rf"{client}([^;]+){current_hash}", output)[0]
    secho(f"Found match: {match}")

    nginx_conf = re.sub(
        rf"{client}([^;]+){current_hash}",
        f"{client}{match}{hash}",
        output,
        flags=re.MULTILINE,
    )

    if client == "auth":
        # \1 capturing group doesn't work
        match = re.findall(rf"{client}([^;]+){current_hash}", output)[0]
        nginx_conf = re.sub(
            rf"default([^;]+){current_hash}",
            f"default{match}{hash}",
            nginx_conf,
            flags=re.MULTILINE,
        )

    string = (
        "kubectl patch configmap app-edge-nginx-conf "
        ' -p=\'{"data": {"nginx.conf":'
        f"{nginx_conf}"
        "}}'"
    )

    secho(run_cmd(string, silent=True))
    ctx.invoke(restart, service="app-edge")
    secho("Done pushing changes", fg="green")
    secho(f"New hashes:\n{run_cmd('khash', silent=True)}")
