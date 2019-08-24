# -*- coding: utf-8 -*-

from troposphere import (
    Sub
)

def service_role_trust_policy(service_name, external_id=None):
    """
    Simple function to format the trust relationship for a Role and an AWS Service
    used from lambda-my-aws/ozone
    """
    statement = {
        "Effect": "Allow",
        "Principal": {
            "Service": [
                Sub(f'{service_name}.${{AWS::URLSuffix}}')
            ]
        },
        "Action": ["sts:AssumeRole"]
    }
    if external_id is not None:
        statement['Condition'] = {}
        statement['Condition']['StringEquals'] = {
            "sts:ExternalId": external_id
        }
    policy_doc = {
        "Version": "2012-10-17",
        "Statement": [
            statement
        ]
    }
    return policy_doc
