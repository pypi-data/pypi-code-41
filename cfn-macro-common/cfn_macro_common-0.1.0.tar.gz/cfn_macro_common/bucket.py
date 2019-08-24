# -*- coding: utf-8 -*-

from os import environ
from boto3 import client
from botocore.exceptions import ClientError


def check_bucket(bucket_name):
    """
    Function that checks if the S3 bucket exists and if not attempts to create it.
    """
    s3_client = client('s3', region_name=environ['AWS_DEFAULT_REGION'])
    try:
        s3_client.head_bucket(
            Bucket=bucket_name
        )
        return True
    except ClientError as error:
        if error.response['Error']['Code'] == '404':
            try:
                s3_client.create_bucket(
                    ACL='private',
                    Bucket=bucket_name,
                    ObjectLockEnabledForBucket=True,
                    CreateBucketConfiguration={
                        'LocationConstraint': environ['AWS_DEFAULT_REGION']
                    }
                )
                return True
            except Exception as error:
                print(error)
                return False
        print(error)
        return False
