import click
from indico_install.utils import options_wrapper
from indico_install.infra.input_utils import download_indicoapi_data, auth_with_gsutil

from indico_install.infra.single_node import single_node
from indico_install.infra.gke import gke
from indico_install.infra.aks import aks

# Here we try and include the EKS function
# It depends on boto3 which may not be installed
# in which case we include a stub instead
try:
    from indico_install.infra.eks import eks
except Exception:
    @click.command("eks")
    def eks():
        """Not available"""
        pass


@click.group("infra")
@click.pass_context
def infra(ctx):
    """
    Indico infrastructure setup and validation. Supports EKS, GKE, and single node installations.

    EKS Note! must install package with "eks" extras for EKS
    """
    pass

@infra.command("download_apidata")
@click.pass_context
@click.argument("version", required=True, type=str)
@click.option("--extract/--no-extract", default=True, show_default=True, help="Automatically extract the downloaded TAR")
@options_wrapper()
def download_api_data(ctx, version, *, extract, deployment_root, **kwargs):
    """
    Download VERSION of API data TAR from google cloud to local --deployment-root.
    Un-tar the file into a directory of the same name, also in the deployment-root
    VERSION is something like "v7".

    Requires Authentication with GSutil to download the TAR, but will attempt to auth with an existing key if it exists.

    Will not download TAR if it already exists.
    Will not extract the TAR if the data directory already exists in --deployment-root
    """
    auth_with_gsutil(deployment_root)
    download_indicoapi_data(deployment_root, version=version, extract=extract)


for command_group in [single_node, gke, eks, aks]:
    infra.add_command(command_group)
