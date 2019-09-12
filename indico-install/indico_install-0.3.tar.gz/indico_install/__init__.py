import click
from .sync import push, pull
from .helm import apply, render, upload, apply_patch, info
from .generate import generate
from .infra import infra
from .kube import pod, svc

command_groups = [
    pull,
    push,
    apply,
    apply_patch,
    render,
    generate,
    infra,
    pod,
    svc,
    upload,
    info,
]


@click.group("indico_cli")
@click.pass_context
def indico_cli(ctx):
    """
    Indico's CLI tool for cluster deployment and management.

    See `indico COMMAND [SUBCOMMAND, ] --help` for more information

    Scripts:

      These are utility scripts encapsulating the most common commands used in cluster management. They come installed with the indico CLI tool.

        kd [PODREGEX='']: describe all pods matching PODREGEX (wraps `kubectl describe pods`). Example: `kd custom-predict`

        kp [PODREGEX='']: list pods matching PODREGEX (wraps `kubectl get pods -o wide`). Example: `kp` or `kp custom`

        klogs [PODREGEX='']: tail logs for pods matching PODREGEX. Example: `klogs custom` or `klogs custom\|moonbow`

        kube exec PODREGEX [COMMAND='bash']: run COMMAND as a TTY in the first pod matching PODREGEX (wraps `kubectl exec -it <pod>`). Example: `kube exec fog`

        kube scale SERVICEREGEX AMOUNT: scale the number of pods for services matching SERVICEREGEX to AMOUNT.
        Will save settings in your input yaml. Alias of `indico svc scale`

        kube update SERVICEREGEX: roll the pods of all services matching SERVICEREGEX. Alias of `indico svc restart`

    """
    ctx.ensure_object(dict)


for command_group in command_groups:
    indico_cli.add_command(command_group)
