"""
This tool is designed to be used via the command line to aid in the discovery and interaction of Lasso EC2 instances.

The output produced is meant to be "clickable" providing a simple way to SSH into into EC2 instances as long as an
existing VPN tunnel is active and that VPN tunnel give the user the correct level of access within AWS.

"""

import fire
import boto3

S3 = boto3.resource('s3')


class Cull(object):
    def ec2(self, cloud: str, service: str):
        """
        Search for EC2 instances using `cloud` and `service` as filters.

        Args:
            cloud: The Lasso operational environment
            service: The Lasso service name

        Returns:
            None, Prints output to std out.
        """

        ec2 = boto3.resource("ec2")

        asc = boto3.client("autoscaling")

        filters = [
            {"Name": "tag:cloud", "Values": [cloud]},
            {"Name": "tag:service", "Values": [service]},
            # make sure instance is running
            {"Name": "instance-state-code", "Values": ["16"]}
        ]

        instance_names = [tag["Value"] for instance in ec2.instances.filter(Filters=filters) for tag in instance.tags if
                          tag["Key"] == "Name"]

        instance_ips = [instance.private_ip_address for instance in ec2.instances.filter(Filters=filters)]

        instance_ids = [
            instance.instance_id for instance in ec2.instances.filter(Filters=filters)]

        asc_instances = asc.describe_auto_scaling_instances(InstanceIds=instance_ids)

        instance_lifecycle_states = {instance.get("InstanceId", {}): instance.get("LifecycleState", {}) for instance in
                                     asc_instances["AutoScalingInstances"]}

        for index, name in enumerate(instance_names):
            print("Name:{0} | ID:{1} | State:{2} | ssh://ubuntu@{3}".format(name, instance_ids[index],
                                                                            instance_lifecycle_states.get(
                                                                                instance_ids[index], {}),
                                                                            instance_ips[index]))


def main():
    fire.Fire(Cull)


if __name__ == '__main__':
    main()
