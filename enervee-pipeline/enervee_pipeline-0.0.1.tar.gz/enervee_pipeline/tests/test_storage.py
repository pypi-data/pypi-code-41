import os
import json
import boto3
import pytest
from moto import mock_s3
import enervee_pipeline.config as config
from enervee_pipeline.storage import Storage

TEST_BUCKET_NAME = 'bucket'
TEST_FOLDER = 'folder'
TEST_ITEM_CONTENT = json.dumps({'product_id': 'test_id'})
TEST_ITEM_ID = '1234'


def get_mocked_storage(s3, bucket_name):
    class MockStorage(Storage):
        def __init__(self, *args):
            self.s3_client = s3
            self.bucket_name = bucket_name

    s3.create_bucket(Bucket=TEST_BUCKET_NAME)
    mock_storage = MockStorage(s3, bucket_name)
    return mock_storage


@pytest.fixture
@mock_s3
def storage():
    s3_client = boto3.client('s3', region_name=config.AWS_REGION)
    test_storage = get_mocked_storage(s3_client, TEST_BUCKET_NAME)
    yield test_storage


@mock_s3
def test_upload_item_to_folder(storage):
    test_storage = storage.__next__()
    content = TEST_ITEM_CONTENT
    item_path = os.path.join(TEST_FOLDER, TEST_ITEM_ID)

    # Test storage class function to upload item
    test_storage.upload_item_to_folder(TEST_ITEM_ID, content, TEST_FOLDER)
    # Use built-in s3 function to download item
    bucket_object = test_storage.s3_client.get_object(Bucket=TEST_BUCKET_NAME, Key=item_path)
    bucket_object_string = bucket_object['Body'].read().decode('utf-8')
    assert bucket_object_string == TEST_ITEM_CONTENT


@mock_s3
def test_download_item_from_folder(storage):
    test_storage = storage.__next__()
    content = TEST_ITEM_CONTENT
    item_path = os.path.join(TEST_FOLDER, TEST_ITEM_ID)

    # Use built-in s3 function to upload item
    test_storage.s3_client.put_object(Body=content, Bucket=TEST_BUCKET_NAME, Key=item_path)
    # Test storage class function to download item
    bucket_object = test_storage.download_item_from_folder(TEST_ITEM_ID, TEST_FOLDER)
    bucket_object_string = bucket_object.decode('utf-8')
    assert bucket_object_string == TEST_ITEM_CONTENT
