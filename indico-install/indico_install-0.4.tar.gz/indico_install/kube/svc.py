from datetime import datetime
import click
from indico_install.utils import run_cmd, options_wrapper
from indico_install.config import ConfigsHolder, merge_dicts
from indico_install.helm import render, apply
from indico_install.setup import get_tls


@click.group("svc")
@click.pass_context
def svc(ctx):
    """Commands for cluster services"""
    pass


@svc.command("update")
@click.pass_context
@click.argument("service", required=True, type=click.Choice(["ssl"]))
@options_wrapper(check_input=True)
def update_svc(ctx, service, *, input_yaml, **kwargs):
    """
    Function to update an existing service.

    Args:

      <SERVICE>: The service to update. Choices are:

        - ssl : update certificates
    """
    if service == "ssl":
        config = ConfigsHolder(config=input_yaml)
        get_tls(config, redo=True)
        ctx.invoke(render, input_yaml=input_yaml, **kwargs)
        ctx.invoke(
            apply, service="app-edge-nginx-conf", input_yaml=input_yaml, **kwargs
        )
        ctx.invoke(restart, service="app-edge")
    else:
        click.secho(f"Service {service} has no update logic.")


@svc.command("scale")
@click.pass_context
@click.argument("service", required=True, type=str)
@click.argument("amount", required=True, type=int)
@options_wrapper()
def scale(ctx, service, amount, *, input_yaml, yes, **kwargs):
    """
    Scale a K8S cluster deployment or statefulset

    ARGS:
        <SERVICE> grep string of deployments and statefulsets to scale

        <AMOUNT> number of pods to create
    """
    updated_svcs = []
    for svc_type in ["deployment", "statefulset"]:
        out = run_cmd(
            """kubectl get %s --no-headers | grep "%s" | awk '{print $1}'"""
            % (svc_type, service),
            silent=True,
        )
        if not out:
            continue
        for _svc in out.splitlines():
            click.secho(
                run_cmd(
                    """kubectl patch %s %s -p '{"spec":{"replicas":%d}}'"""
                    % (svc_type, _svc, amount)
                ),
                fg="green",
            )
            updated_svcs.append(_svc)

    if updated_svcs and yes:
        if not input_yaml.is_file():
            click.secho(
                f"Could not find {input_yaml}. Unable to save new scale", fg="yellow"
            )
            return
        conf = ConfigsHolder(config=input_yaml)
        updated_svcs_dict = {
            _svc: {"values": {"replicas": amount}} for _svc in updated_svcs
        }
        conf["services"] = merge_dicts(conf.get("services", {}), updated_svcs_dict)
        conf.save()


@svc.command("restart")
@click.pass_context
@click.argument("service", required=True)
def restart(ctx, service):
    """
    Reroll a K8S cluster deployment or statefulset.

    ARGS:

        <SERVICE> grep string of deployments and statefulsets to reroll

         - "all" reset all deployments and statefulsets with an inditype label of service or celerytask
    """
    patch_string = '{"spec":{"template":{"metadata":{"labels":{"date":"%d"}}}}}' % (
        int(datetime.now().timestamp())
    )
    for svc_type in ["deployment", "statefulset"]:
        if service == "all":
            out = run_cmd(
                """kubectl get %s -l 'inditype in (service, celerytask)' --no-headers | awk '{print $1}' | xargs -n 1 -I {} kubectl patch %s {} -p '%s'"""
                % (svc_type, svc_type, patch_string),
                silent=True,
            )
        else:
            out = run_cmd(
                """kubectl get %s --no-headers | grep "%s" | awk '{print $1}' | xargs -n 1 -I {} kubectl patch %s {} -p '%s'"""
                % (svc_type, service, svc_type, patch_string),
                silent=True,
            )
        if out:
            click.secho(out, fg="green")
