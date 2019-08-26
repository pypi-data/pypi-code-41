import boto3


def push_to_kinesis(stream_name):
    client = boto3.client('kinesis')
    response = client.put_records(
        Records=[
            {
                'Data': b'bytes',
                'ExplicitHashKey': 'string',
                'PartitionKey': 'string'
            },
        ],
        StreamName=stream_name
    )