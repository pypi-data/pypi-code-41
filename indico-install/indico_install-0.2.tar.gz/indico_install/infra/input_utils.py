import tarfile
from pathlib import Path

from click import prompt, secho

from indico_install.utils import convertb64, run_cmd, find_gcs_key


def auth_with_gsutil(deployment_root, raise_missing_key=False):
    gcs_key = find_gcs_key(deployment_root)
    if not gcs_key:
        if raise_missing_key:
            raise AssertionError("Unable to find a key for Google auth")
        else:
            return

    authed = run_cmd(f"gcloud auth activate-service-account --key-file={gcs_key} 2>&1", silent=True)
    return "Activated service account" in authed


def postgres_input(conf):
    db_details = conf["postgres"]["app"]
    host = prompt("What is your DB endpoint?", type=str, default=db_details.get("host"))
    user = prompt("What is your DB user?", type=str, default=db_details.get("user"))
    password = prompt(
        "What is your DB password? Type 'USE OLD' to use existing pw.",
        hide_input=True,
        confirmation_prompt=True,
        default="USE OLD" if db_details.get("password") else None,
    )
    password = (
        db_details.get("password") if password == "USE OLD" else convertb64(password)
    )
    conf["postgres"]["app"].update({"host": host, "password": password, "user": user})
    conf["postgres"]["custom"].update(
        {"host": host, "password": password, "user": user}
    )


def download_indicoapi_data(deployment_root, version=None, extract=True):
    indicoapi_version = version or prompt("Version of api model data to download", default="v7")
    indicoapi_tar = f"indicoapi_data_{indicoapi_version}.tar.gz"

    tar_path = Path(deployment_root) / indicoapi_tar
    data_path = Path(deployment_root) / f"indicoapi_data_{indicoapi_version}"
    if not data_path.exists():
        if tar_path.exists():
            secho(f"Skipping download - using {tar_path}", fg="yellow")
        else:
            run_cmd(
                f"mkdir -p {data_path} && gsutil cp gs://indicoapi-data/{indicoapi_tar} {deployment_root}"
            )
            assert tar_path.exists(), "Unable to download indicoapi_data successfully"
        if extract:
            tar = tarfile.open(tar_path, "r:gz")
            tar.extractall(path=data_path)
            tar.close()
            secho(f"Unzipped data to {data_path}", fg="green")
        else:
            secho("Please extract and upload TAR {tar_path} when ready")
            return
    else:
        secho(
            f"Skipping indicoapi data download - already exists at {data_path}",
            fg="yellow",
        )

    return data_path
