import os
from functools import wraps

import boto3
from cached_property import cached_property
from click import prompt

from indico_install.config import merge_dicts
from indico_install.infra.input_utils import postgres_input

access_key = os.getenv("AWS_ACCESS_KEY_ID")
access_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
aws_profile = os.getenv("AWS_PROFILE") or os.getenv("AWS_DEFAULT_PROFILE")


def ask_for_infra_input(conf):
    """
    Conf is a full dictionary
    Root is the key path we've followed to get to conf
    ask_all is whether or not to re-ask for input for existing values
    """
    gw_details = conf["clusterVolumes"]["rwx"]["nfs"]
    gateway_ip = prompt(
        f"What is your gateway IP?", type=str, default=gw_details.get("server")
    )

    client_bucket_name = prompt(
        f"What is the name of your S3 bucket?",
        type=str,
        default=gw_details.get("path")[1:] if gw_details.get("path") else None,
    )

    conf["clusterVolumes"]["rwx"]["nfs"] = {
        "server": gateway_ip,
        "path": f"/{client_bucket_name}",
    }
    conf["clusterVolumes"]["rox"]["nfs"] = {
        "server": gateway_ip,
        "path": "/indico-platform-clients",
    }

    postgres_input(conf)

    cluster_name = prompt(
        "What is the name of your EKS cluster?",
        type=str,
        default=conf.get("cluster", {}).get("name"),
    )
    cluster_asg = prompt(
        "What is the name of your ASG group?",
        type=str,
        default=conf.get("cluster", {}).get("nodegroup_name"),
    )
    internal_elb_annotation = "service.beta.kubernetes.io/aws-load-balancer-internal"
    cluster_private = prompt(
        "Is your cluster private?",
        type=bool,
        default=internal_elb_annotation
        in conf.get("services", {}).get("app-edge", {}).get("values", {}).get("annotations", {}),
    )
    if cluster_private:
        conf["services"] = merge_dicts(
            conf.get("services", {}),
            {
                "app-edge": {
                    "values": {
                        "annotations": {
                            "service.beta.kubernetes.io/aws-load-balancer-internal": "0.0.0.0/0"
                        }
                    }
                }
            },
        )
    else:
        conf.get("services", {}).get("app-edge", {}).get("values", {}).get("annotations", {}).pop(internal_elb_annotation, None)

    conf["cluster"] = {"name": cluster_name, "nodegroup_name": cluster_asg}
    return conf


def session(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        kwargs = kwargs or {}
        if not kwargs.get("session"):
            kwargs["session"] = Session()
        return f(*args, **kwargs)

    return wrapper


class Session(object):
    if not ((access_key and access_secret) or aws_profile):
        _boto_session = None
    else:
        _boto_session = boto3.session.Session(
            region_name=aws_region,
            aws_access_key_id=access_key,
            aws_secret_access_key=access_secret,
            profile_name=aws_profile,
        )

    @cached_property
    def ASGClient(cls):
        return cls._boto_session.client("autoscaling")

    @cached_property
    def EC2Client(cls):
        return cls._boto_session.client("ec2")

    @cached_property
    def EC2Resource(cls):
        return cls._boto_session.resource("ec2")

    @cached_property
    def EKSClient(cls):
        return cls._boto_session.client("eks")

    @cached_property
    def IAMClient(cls):
        return cls._boto_session.client("iam")

    @cached_property
    def IAMResource(cls):
        return cls._boto_session.resource("iam")

    @cached_property
    def RDSClient(cls):
        return cls._boto_session.client("rds")

    @cached_property
    def S3Client(cls):
        return cls._boto_session.client("s3")

    @cached_property
    def SGWClient(cls):
        return cls._boto_session.client("storagegateway")
