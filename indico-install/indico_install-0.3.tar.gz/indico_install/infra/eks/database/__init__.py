from indico_install.infra.eks.config import session
from indico_install.utils import run_cmd, decodeb64


@session
def validate(config, session=None):
    """
    Validates the following:
    - RDS database for postgres has a certain instance size
    - db is configured with parallel workers
    - does not validate Redis (we assume in-cluster here)
    """
    info = config["postgres"]["app"]
    assert info.get("host"), "Database info not provided"
    try:
        db = session.RDSClient.describe_db_instances(Filters=[{
            "Name": "db-instance-id",
            "Values": [info["host"].split('.')[0]]
        }])[
            "DBInstances"
        ][0]
    except Exception:
        raise Exception("Unable to locate database")

    assert "postgres" in db["Engine"].lower(), "DB not a postgres instance!"
    assert db["DBInstanceStatus"] == "available"
    if "aurora" not in db["Engine"].lower():
        # Aurora DBs are dynamically provisioned
        assert db["AllocatedStorage"] >= 500, "DB must have at least 500GB of storage"
    assert (
        "xlarge" in db["DBInstanceClass"]
    ), "Database instance must be at least an xlarge"
    param_groups = [
        p["DBParameterGroupName"]
        for p in db["DBParameterGroups"]
        if p["ParameterApplyStatus"] == "in-sync"
    ]

    all_params = {}
    params_we_want = {
        "max_worker_processes": {"fn": lambda x: x and int(x) >= 80, "doc": ">= 80"},
        "force_parallel_mode": {"fn": lambda x: x and int(x) == 1, "doc": "== 1"},
        "max_parallel_workers_per_gather": {"fn": lambda x: x and int(x) >= 16, "doc": ">= 16"}
    }

    paginator = session.RDSClient.get_paginator("describe_db_parameters")
    for pg in param_groups:
        param_pages = paginator.paginate(DBParameterGroupName=pg)
        for page in param_pages:
            all_params.update(
                {
                    p["ParameterName"]: p.get("ParameterValue")
                    for p in page["Parameters"]
                    if p["ParameterName"] in params_we_want
                }
            )
    bad_params = [k for k, v in all_params.items() if not params_we_want[k]["fn"](v)]
    assert not bad_params, ", ".join(
        [f"{k} is not {params_we_want[k]['doc']}" for k in bad_params]
    )
    check_database(info)


def check_database(info):
    # ask for user, password, db_name to connect to
    host = info["host"]
    user = info["user"]
    password = info["password"]
    db_name = "indico"
    assert run_cmd(
        "which psql", silent=True
    ).strip(), (
        "psql not found on machine - cannot validate db connection. please install the postgresql-client and retry"
    )

    psql_command = f"PGPASSWORD={decodeb64(password)} psql -h {host} -p 5432 -U {user} {db_name} --list --tuples-only"
    output = run_cmd(psql_command, silent=True)
    tables = {}
    for line in output.splitlines():
        db, owner = [val.strip() for val in line.split(" | ")[:2]]
        tables.update({db: owner} if db else {})

    all_dbs = [
        "crowdlabel",
        "cyclone",
        "elmosfire",
        "moonbow",
        "noct",
    ]

    not_found = [db for db in all_dbs if db not in tables]
    assert (
        not not_found
    ), f"The following databases do not exist in your database: {not_found}"
