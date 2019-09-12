from pathlib import Path
import copy
import os
import re
import tempfile
from contextlib import contextmanager

import click

from indico_install.config import (
    ConfigsLoader,
    merge_dicts,
    REMOTE_TEMPLATES_PATH,
    yaml,
)
from indico_install.setup import setup
from indico_install.utils import run_cmd, options_wrapper

var_regex = re.compile(r"<\!var:([^<>]*)>")
lookup_regex = re.compile(r"<\!lookup:([^<>]*)>")


@contextmanager
def _resolve_values(values):
    f = tempfile.NamedTemporaryFile(mode="w")
    yaml.dump(dict(values.items()), f, default_flow_style=False)
    yield f" -f {f.name}"
    f.close()


def _resolve_template(template_values, variables, conf):
    if isinstance(template_values, dict):
        new_values = {}
        for key, value in template_values.items():
            new_values[_resolve_template(key, variables, conf)] = _resolve_template(
                value, variables, conf
            )
        return new_values
    elif isinstance(template_values, list):
        return [_resolve_template(value, variables, conf) for value in template_values]
    elif isinstance(template_values, str):
        var_matches = var_regex.findall(template_values)
        lookup_matches = lookup_regex.findall(template_values)
        while var_matches or lookup_matches:
            for match in var_matches:
                parts = match.split("=", 1)
                if len(parts) > 1:
                    default = str(parts[1])
                else:
                    default = ""
                template_values = template_values.replace(
                    f"<!var:{match}>", str(variables.get(parts[0], default))
                )
            for match in lookup_matches:
                look_up_keys = match.split("|")
                target_value = dict(conf)
                parts = look_up_keys[-1].split("=", 1)
                if len(parts) > 1:
                    default = str(parts[1])
                    look_up_keys[-1] = parts[0]
                else:
                    default = ""
                for look_up_key in look_up_keys:
                    target_value = target_value.get(look_up_key, {})
                template_values = template_values.replace(
                    f"<!lookup:{match}>", str(target_value) if target_value != {} else default
                )
            var_matches = var_regex.findall(template_values)
            lookup_matches = lookup_regex.findall(template_values)

    return template_values


def helm_render(deployment_root, templates_dir, group, template, values, values_files=""):
    generated_dir = deployment_root / "generated"
    click.echo(f"Generating {values['name']}.yaml")
    with _resolve_values(values) as resolved_str:
        results = run_cmd(
            f"helm template {values_files} {templates_dir / group} --execute templates/{template}.yaml{resolved_str}",
            silent=True,
        )

    with open(generated_dir / f"{values['name']}.yaml", "w") as f:
        f.write(results)


def resolve_templates(templates):
    unresolved_templates = lambda: {
        template_name: template
        for template_name, template in templates.items()
        if "<!template>" in template
    }
    templates_to_resolve = unresolved_templates()
    while templates_to_resolve:
        for template_name, template in templates_to_resolve.items():
            template_to_merge = template.pop("<!template>")
            templates[template_name] = merge_dicts(
                copy.deepcopy(templates[template_to_merge]), templates[template_name]
            )
        templates_to_resolve = unresolved_templates()


def resolve_all(configs):
    resolve_templates(configs["_templates"])

    for resource, helm_info in configs["services"].items():
        if "<!template>" in helm_info:
            template_name = helm_info.pop("<!template>")
            configs["services"][resource] = merge_dicts(
                copy.deepcopy(configs["_templates"][template_name]), helm_info
            )
            # Attach additional values
        configs["services"][resource]["values"] = configs["services"][resource].get(
            "values", {}
        )
        configs["services"][resource] = _resolve_template(
            configs["services"][resource], configs["services"][resource], configs
        )

    configs.update(
        _resolve_template(
            {k: v for k, v in configs.items() if k not in ("_templates", "services")},
            {},
            configs,
        )
    )



def render_from_local(deployment_root, templates_dir, cluster, services_yaml, input_yaml, service=None):
    generated = deployment_root / "generated"
    click.secho(f"clearing {generated}", fg="yellow")
    os.makedirs(generated, exist_ok=True)
    run_cmd(f"rm -rf {generated/ '*.yaml'}", silent=True)

    setup(input_yaml)
    # images will be "updated" by Indico and contains cluster defaults
    # input is customer overrides
    configs = ConfigsLoader(services_yaml, input_yaml)
    resolve_all(configs)

    with _resolve_values(configs) as resolved_str:
        for resource, helm_info in configs["services"].items():
            if service and service not in resource:
                continue

            helm_info["values"] = helm_info.get("values", {})
            helm_info["values"]["name"] = resource
            configs["services"][resource] = helm_info
            if helm_info.pop("<!disabled>", None):
                continue
            extra_keys = {
                k: v
                for k, v in helm_info.items()
                if k not in ("group", "template", "values")
            }
            helm_info["values"] = merge_dicts(extra_keys, helm_info["values"])
            [helm_info.pop(k) for k in extra_keys.keys()]

            helm_render(deployment_root, templates_dir, values_files=f" {resolved_str}", **helm_info)

    configs.save(deployment_root / "configuration" / f"{cluster}.yaml")


def _resolve_remote(deployment_root, remote_path):
    """
    Download remote templates and services yaml and unpack
    Unpack if necessary, and validate contents (error if validation fails)
    Return the location of the local, unpacked templates dir
    """
    remote_templates_path = REMOTE_TEMPLATES_PATH + remote_path + "/templates.tar.gz"
    remote_services_yaml = REMOTE_TEMPLATES_PATH + remote_path + "/services.yaml"
    local_directory = deployment_root / "remote_configs" / ''.join(c for c in str(remote_path) if c.isalnum)
    click.secho(f"Downloading remote configs to {local_directory}", fg="yellow")
    if local_directory.is_dir():
        run_cmd(f"rm -rf {local_directory}", silent=True)
    os.makedirs(local_directory / "templates", exist_ok=True)

    run_cmd(f"wget {remote_templates_path} -O - | tar -xz -C {local_directory / 'templates'}")
    run_cmd(f"wget {remote_services_yaml} -O {local_directory / 'services.yaml'}")
    return (local_directory / "services.yaml", local_directory / "templates")


@click.command("render")
@click.pass_context
@click.argument("service", required=False)
@click.option("-r", "--remote-configs", help="Remote GCS folder with configs to render from. Ex: 'latest' or 'master.24235243'")
@options_wrapper(check_input=True)
def render(ctx, service=None, *, deployment_root, cluster, input_yaml, services_yaml, remote_configs, **kwargs):
    """
    Render Helm templates from the "templates" directories.

    Only render the template for services with names containing <SERVICE> if provided
    """
    deployment_root = Path(deployment_root)
    templates_dir = deployment_root / "templates"
    if remote_configs:
        services_yaml, templates_dir = _resolve_remote(deployment_root, remote_configs)

    if not services_yaml.is_file():
        click.secho(f"Could not find {services_yaml}.", fg="red")
        return

    render_from_local(deployment_root, templates_dir, cluster, services_yaml, input_yaml, service=service)
    click.secho("All set!", fg="green", bold=True)
