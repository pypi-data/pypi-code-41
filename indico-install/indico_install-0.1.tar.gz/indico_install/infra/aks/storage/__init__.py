import json
from click import secho
from indico_install.utils import run_cmd
from indico_install.infra.input_utils import download_indicoapi_data

FILE_SHARE_SECRET_NAME = "azure-storage-key"


def create(deployment_root, conf, upload=False):
    if upload:
        upload_indicoapi_data(deployment_root, conf)
    storage_acct_name = conf["cluster"]["storage_acct"]
    storage_acct_key = conf["cluster"]["storage_acct_key"]
    run_cmd(
        f"kubectl create secret generic {FILE_SHARE_SECRET_NAME} "
        f"--from-literal=azurestorageaccountname={storage_acct_name} "
        f"--from-literal=azurestorageaccountkey={storage_acct_key}"
    )


def upload_indicoapi_data(deployment_root, conf):
    data_path = download_indicoapi_data()
    cluster_info = conf["cluster"]
    api_data_fs = conf["clusterVolumes"]["rox"]["azureFile"]["shareName"]

    secho(f"Uploading data to Azure file share {api_data_fs}", fg="yellow")
    run_cmd(
        f"az storage file upload-batch --account-name {cluster_info['storage_acct']} "
        f"--account-key {cluster_info['storage_acct_key']} "
        f"-d {api_data_fs} -s {data_path} --max-connections 10"
    )
    secho("Upload complete!", fg="green")


def check(conf):
    cluster_info = conf["cluster"]
    api_data_fs = conf["clusterVolumes"]["rox"]["azureFile"]["shareName"]
    out = run_cmd(
        f"az storage file list --account-name {cluster_info['storage_acct']} "
        f"--account-key {cluster_info['storage_acct_key']} -s {api_data_fs}"
    )
    api_files = [f["name"] for f in json.loads(out)]
    assert (
        len(api_files) > 6 and "finetune_models" in api_files
    ), "Files have not been correctly uploaded to the indicoapi file share"
