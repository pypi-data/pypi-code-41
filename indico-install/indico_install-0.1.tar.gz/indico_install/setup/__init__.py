import os
import uuid
from click import secho, prompt, confirm

from indico_install.config import ConfigsHolder
from indico_install.utils import base64file, find_values, convertb64, run_cmd, find_gcs_key


def configure_passwords(configs):
    """Generate secrets for <generate_secret> inputs"""
    for _dict, key, _ in find_values(configs, "<generate_secret>"):
        _dict[key] = convertb64(uuid.uuid4().hex[:32])

    configs.save()

def configure_gcr_key(deployment_root):
    if run_cmd("kubectl get secrets | grep gcr-pull-secret", silent=True):
        return

    key_file = find_gcs_key(deployment_root)
    if not key_file:
        return

    secho("Generating gcr-pull-secret", fg="yellow")
    client_name = key_file[4:-5]
    out = run_cmd(
        (
            'kubectl create secret docker-registry gcr-pull-secret '
            '--docker-server=https://gcr.io --docker-username=_json_key '
            f'--docker-password="$(cat {deployment_root}/gcr-{client_name}.json)" '
            f'--docker-email="gcr-{client_name}@new-indico.iam.gserviceaccount.com"'
        ), silent=True
    )
    secho(f"{out}\n", fg="green")


def get_tls(configs, redo=False):
    if not redo and all([v for v in configs["tls"].values()]):
        return
    cert_file = configs["tls"].get("certfile")
    key_file = configs["tls"].get("keyfile")

    secho("Ctrl-C will skip the prompt.", fg="blue")

    try:
        ok = False
        while not ok:
            cert_file = os.path.abspath(prompt("SSL Cert File", default=cert_file if cert_file else None))
            ok = confirm(f"Is this the file? {cert_file}")
        configs["tls"]["cert"] = base64file(cert_file)
        configs["tls"]["certfile"] = cert_file
    except Exception:
        secho("Invalid ssl cert file", fg="red")
        return

    try:
        ok = False
        while not ok:
            key_file = os.path.abspath(prompt("SSL Key File", default=key_file if key_file else None))
            ok = confirm(f"Is this the file? {key_file}")
        configs["tls"]["key"] = base64file(key_file)
        configs["tls"]["keyfile"] = key_file
    except Exception:
        secho("Invalid ssl key file", fg="red")
        return

    configs.save()


def setup(input_yaml):
    """
    Set up your initial environment using an interactive yaml form
    """

    configs = ConfigsHolder(config=input_yaml)
    configure_passwords(configs)

    for k in ["parentDomain", "publicDomain"]:
        if not configs.get(k):
            configs[k] = prompt(k)
    configs.save()

    get_tls(configs)
