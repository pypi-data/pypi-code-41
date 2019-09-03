import boto3


def _session(aws_access_key_id, aws_secret_access_key, aws_region_name):
    return boto3.session.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region_name)


def s3_client(aws_access_key_id, aws_secret_access_key, aws_region_name):
    return _session(aws_access_key_id, aws_secret_access_key, aws_region_name).client('s3')
