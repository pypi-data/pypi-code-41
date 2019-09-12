import uuid
import tempfile
import time
from pathlib import Path

import click
import yaml

from indico_install.config import ConfigsHolder, merge_dicts
from indico_install.helm.upload import upload
from indico_install.helm.render import _resolve_remote, render
from indico_install.setup import configure_gcr_key
from indico_install.utils import options_wrapper, run_cmd, current_user


def diff_files(f1, f2):
    diff_out = run_cmd(f"diff {f1} {f2}", silent=True)
    for line in diff_out.splitlines():
        if line.startswith("+"):
            click.secho(line, fg="green")
        elif line.startswith("-"):
            click.secho(line, fg="red")
        else:
            click.echo(line)

class Deployment():
    def __init__(self):
        self.key = str(uuid.uuid4())
        self.start = time.time()
        self.user = current_user()

    def get_deployment_version_data(self):
        curr_vers = run_cmd(
            "kubectl get configmap deployed-version -o yaml 2>&1", silent=True
        )
        assert (
            "NotFound" not in curr_vers
        ), "Configmap for current version not found! Please indico apply to initialize the cluster"
        return yaml.safe_load(curr_vers)["data"]


    def set_deployment_version(self, services_yaml_version, templates_version=None):
        run_cmd(
            """kubectl patch configmap deployed-version -p '{"data":{"services.yaml": "%s","templates": "%s","updated_by":"%s", "last_updated":"%s"}}'"""
            % (services_yaml_version, templates_version or services_yaml_version, self.user, time.strftime('%m/%d/%y %H:%M:%S %z', time.localtime(self.start)))
        )


    def is_version_locked(self):
        # lock exists, wasn't set by us, and is less than 10 min old
        curr_lock = self.get_deployment_version_data().get("lock", {})
        return curr_lock and curr_lock["applied_by"] != self.key and int(self.start - int(curr_lock["time"])) < 10 * 60


    def set_deployment_lock(self, remove=False, wait=0):
        while wait:
            if self.is_version_locked():
                time.sleep(1)
                wait -= 1
            else:
                break
        assert not self.is_version_locked(), "deploymet is already locked"
        lock_val = "null" if remove else '{"applied_by":"%s","time":"%d"}' % (self.key, self.start)
        run_cmd(
            """kubectl patch configmap deployed-version -p '{"data":{"lock":%s}}'"""
            % lock_val,
            silent=True,
        )


@click.command("info")
@click.pass_context
def info(ctx):
    """
    Grab the deployed-version configmap
    for information on the state of the cluster
    """
    click.echo(Deployment().get_deployment_version_data())


@click.command("apply-patch")
@click.pass_context
@click.option("-f", "--patch-file", required=True, help="Patch file to apply")
@click.option("-w", "--wait", type=int, default=0, show_default=True, help="Seconds to wait for deploymewnt to unlock")
@options_wrapper(check_input=True)
def apply_patch(ctx, patch_file=None, wait=0, *, deployment_root, yes, **kwargs):
    """
    Apply a patch to the current services - this will NOT override params in cluster.yaml
    Example patch yaml to update the moonbow image for all moonbow services

      images: {moonbow: moonbow:development.32532464564574637}
    """
    if not Path(patch_file).is_file():
        click.secho(f"Could not find patch file {patch_file}", fg="red")
        return
    dep = Deployment()
    curr_vers = dep.get_deployment_version_data()
    # curr_vers = {"services.yaml": "development", "templates": "development"}
    dep.set_deployment_lock(wait=wait)

    try:
        with open(patch_file, "r") as f:
            patches = yaml.safe_load(f)

        services_yaml, templates_dir = _resolve_remote(
            Path(deployment_root), curr_vers["services.yaml"]
        )
        new_services_file = Path(tempfile.gettempdir()) / "services.yaml"
        run_cmd(f"cp {services_yaml} {new_services_file}")
        new_services = ConfigsHolder(new_services_file)
        new_services.update(merge_dicts(new_services, patches))
        new_services.save()
        diff_files(services_yaml, new_services_file)

        if yes or click.confirm("Apply changes?"):
            run_cmd(f"mv {new_services_file} {services_yaml}", silent=True)

            new_version = f"{dep.start}_{dep.user}"

            versions = ctx.invoke(
                upload,
                tag=[new_version],
                deployment_root=templates_dir.parent,
                services_yaml=services_yaml,
            )
            new_version = versions[0]
            ctx.invoke(
                render, deployment_root=deployment_root, remote_configs=new_version
            )
            ctx.invoke(apply, deployment_root=deployment_root, yes=True, **kwargs)
            dep.set_deployment_version(new_version)
    finally:
        dep.set_deployment_lock(remove=True)


@click.command("apply")
@click.pass_context
@click.argument("service", required=False)
@options_wrapper()
def apply(ctx, service=None, deployment_root=None, yes=False, **kwargs):
    """
    Apply templates in the "generated/" directory.
    Apply only the template files matching <SERVICE> if provided.
    Creates the image pull secret if missing.
    Performs a dry-run for confirmation before applying. Skip dry-run with --yes
    """
    generated_dir = Path(deployment_root) / "generated"
    if not generated_dir.is_dir():
        click.secho(f"'generated/' directory not found in {deployment_root}")
        return
    configure_gcr_key(deployment_root)
    if service is not None:
        templates = run_cmd(
            f"ls {generated_dir} | grep '{service}'", silent=True
        ).splitlines()
        for t in templates:
            results = run_cmd(
                f"kubectl apply -f {generated_dir / t} --dry-run 2>&1 | grep -v 'support dry-run'"
            )

        if yes or click.confirm("Ready to apply these changes?"):
            [run_cmd(f"kubectl apply -f {generated_dir / t}") for t in templates]
    else:
        results = run_cmd(
            f"kubectl apply -R -f {generated_dir} --dry-run 2>&1 | grep -v 'support dry-run'",
            silent=True,
        )
        click.echo("\n".join(results.split(",")) + "\n")

        if yes or click.confirm("Ready to apply these changes?"):
            out = run_cmd(f"kubectl apply -R -f {generated_dir}", silent=True)
            for line in out.splitlines():
                color = "red"
                if "unchanged" in line:
                    color = "yellow"
                elif "configured" in line or "created" in line:
                    color = "green"
                click.secho(line, fg=color)
