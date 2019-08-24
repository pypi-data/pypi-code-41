# -*- coding: utf-8 -*-

"""
Functions to manage a template and wheter it should be stored in S3
"""
from datetime import datetime as dt
import boto3


def upload_template(bucket, file_name, template_body, use_date=True):
    """
    Args:
      bucket: name of the s3 bucket whereto upload the file
      the name of the file in S3
      template_body: the body of the template for CFN
    Returns:
      the URL to the file in S3 if successful, None if upload failed
    """
    date = dt.utcnow().strftime('%Y/%m/%d')
    if use_date:
        key = f'{date}/{file_name}'
    else:
        key = file_name
    client = boto3.client('s3')
    try:
        client.put_object(
            Body=template_body,
            Key=key,
            Bucket=bucket,
            ContentEncoding='utf-8',
            ContentType='application/x-yaml',
            ServerSideEncryption='AES256'
        )
        url_path = f'https://s3.amazonaws.com/{bucket}/{key}'
        return url_path
    except Exception as error:
        print(error)
        return None
