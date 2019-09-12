from indico_install.infra.eks.config import session

from indico_install.utils import run_cmd


@session
def validate(config, session=None):
    """
    Validates the following:
    Cluster is in healthy status
    Nodes are up and connected
    ASG configuration includes:
     - sufficient volume size
     - NFS mount commands in startup scripts
    NOT IMPLEMENTED: Current machine has kubectl access
    """
    info = config.get("cluster")
    assert info, "No cluster information provided"
    cluster = session.EKSClient.describe_cluster(name=info["name"])["cluster"]
    assert cluster["status"] == "ACTIVE", "Cluster is not ACTIVE"

    try:
        asg = session.ASGClient.describe_auto_scaling_groups(
            AutoScalingGroupNames=[info["nodegroup_name"]]
        )["AutoScalingGroups"][0]
    except Exception:
        raise Exception(f"Unable to find node group of name {info['nodegroup_name']}")
    assert asg["DesiredCapacity"] >= 2, "Minimum 2 nodes required"
    assert asg["MinSize"] >= 2, "Minimum 2 nodes must be up"
    assert asg["MaxSize"] > max(
        asg["MinSize"], asg["DesiredCapacity"]
    ), "Max size of ASG must be greater than min size and desired capacity"
    assert (
        len(asg["Instances"]) == asg["DesiredCapacity"]
    ), "There are less nodes in the ASG than the desired capacity"
    assert all(
        [n["HealthStatus"] == "Healthy" for n in asg["Instances"]]
    ), "Some instances are not currently healthy"

    if asg["Instances"][0].get("LaunchConfigurationName"):
        _val_launch_config(asg, session=session)
    else:
        _val_launch_template(asg, session=session)

    # Check the cluster via kubectl
    assert (
        int(run_cmd("kubectl get nodes --no-headers | wc -l", silent=True) or "0") >= asg["DesiredCapacity"]
    ), "Some nodes have not joined the cluster"

    # Now we check to make sure GPU is enabled within the cluster
    nvidia_pods = run_cmd(
        "kubectl get pods --all-namespaces | grep 'nvidia' | grep 'Running'", silent=True
    ).strip()
    assert nvidia_pods != "", "The cluster does not have NVIDIA GPU pods running."


def _val_launch_template(asg, session):
    launch_temp_name = asg["LaunchTemplate"]["LaunchTemplateName"]

    launch_temp_ver = asg["LaunchTemplate"]["Version"]
    assert all(
        [
            n["LaunchTemplate"]["LaunchTemplateName"] == launch_temp_name
            and n["LaunchTemplate"]["Version"] == launch_temp_ver
            for n in asg["Instances"] if n["LifecycleState"] == "InService"
        ]
    ), f"Nodes are not all using the same launch template and version {launch_temp_name} , version {launch_temp_ver} - some may be out of date"

    try:
        launch_template = session.EC2Client.describe_launch_template_versions(
            LaunchTemplateName=launch_temp_name,
            Versions=[launch_temp_ver]
        )["LaunchTemplateVersions"][0]["LaunchTemplateData"]
    except Exception:
        raise AssertionError("Could not find launch template for asg")

    assert launch_template["InstanceType"].startswith("p") and launch_template[
        "InstanceType"
    ].endswith(
        "xlarge"
    ), "Instance types for ASG must be either p2 or p3, and xlarge or larger"
    assert any(
        [
            bdm["Ebs"]["VolumeSize"] >= 100
            for bdm in launch_template["BlockDeviceMappings"]
        ]
    ), "ASG launch template does not specify an EBS volume of at least 100GB for instances"


def _val_launch_config(asg, session):
    assert all(
        [
            n["LaunchConfigurationName"] == asg["LaunchConfigurationName"]
            for n in asg["Instances"]
        ]
    ), "Nodes are not all using the same launch config - some may be out of date"

    # Check how the nodes are configured
    try:
        launch_config = session.ASGClient.describe_launch_configurations(
            LaunchConfigurationNames=[asg["LaunchConfigurationName"]]
        )["LaunchConfigurations"][0]
    except Exception:
        raise AssertionError("Unable to find launch config for autoscaling group")
    assert launch_config["InstanceType"].startswith("p") and launch_config[
        "InstanceType"
    ].endswith(
        "xlarge"
    ), "Instance types for ASG must be either p2 or p3, and xlarge or larger"
    assert any(
        [
            bdm["Ebs"]["VolumeSize"] >= 100
            for bdm in launch_config["BlockDeviceMappings"]
        ]
    ), "ASG launch config does not specify an EBS volume of at least 100GB for instances"
