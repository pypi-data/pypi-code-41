# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 14:21:51 2019

@author: Krishna
"""

import boto3
import ast


def get_secret(secret_name,region_name,aws_key,aws_secret):
    secret_name = secret_name 
    region_name = region_name

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
        aws_access_key_id = aws_key, 
        aws_secret_access_key = aws_secret #
    )
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except:
        raise "Error"
        
    return ast.literal_eval(get_secret_value_response['SecretString'])

