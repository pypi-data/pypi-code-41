import json
import os
from datetime import datetime

import boto3 as boto3
import pytest
import pytz


@pytest.fixture(params=[datetime.utcnow(), datetime(1950, 6, 12), datetime(2525, 4, 1), datetime(1812, 1, 1)])
def correctly_done_dates(request):
    params = request.param
    return pytz.utc.localize(params)


@pytest.fixture(params=[datetime.utcnow(), datetime(1950, 6, 12), datetime(2525, 4, 1), datetime(1812, 1, 1)])
def naive_dates(request):
    params = request.param
    return params


@pytest.fixture(params=[datetime.utcnow(), datetime(1950, 6, 12), datetime(2525, 4, 1), datetime(1812, 1, 1)])
def naive_datetime_packages(request):
    params = request.param
    params = pytz.utc.localize(params)
    return json.dumps({"_alg_class": "datetime", "value": {"tz": None, "timestamp": params.timestamp()}})


@pytest.fixture
def lambda_environment():
    client = boto3.Session(profile_name='dev').client('sts')
    lambda_role = 'arn:aws:iam::726075243133:role/worker-leech-dev-2-Oyster-168YECYUUDQMK'
    response = client.assume_role(
        RoleArn=lambda_role,
        RoleSessionName='lambdaTest'
    )
    credentials = response['Credentials']
    os.environ['AWS_ACCESS_KEY_ID'] = credentials['AccessKeyId']
    os.environ['AWS_SECRET_ACCESS_KEY'] = credentials['SecretAccessKey']
    os.environ['AWS_SESSION_TOKEN'] = credentials['SessionToken']
