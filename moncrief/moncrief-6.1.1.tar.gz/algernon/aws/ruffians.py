import boto3

from algernon.aws.operator import lookup_resource
from algernon.serializers import AlgJson


def start_machine(machine_name, input_kwargs):
    client = boto3.client('stepfunctions')
    input_string = AlgJson.dumps(input_kwargs)
    machine_arn = lookup_resource(machine_name)
    response = client.start_execution(
        stateMachineArn=machine_arn,
        input=input_string
    )
