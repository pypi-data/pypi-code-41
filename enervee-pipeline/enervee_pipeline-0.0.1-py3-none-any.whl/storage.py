import os
import boto3
from enervee_pipeline import config
import logging

LOGGER = logging.getLogger(config.LOGGER_NAME)


class Storage(object):
    def __init__(self, bucket_name):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_REGION,
        )
        self.bucket_name = bucket_name

    def upload_item_to_folder(self, item_id, content, folder):
        item_path = os.path.join(folder, item_id)
        self.s3_client.put_object(Body=content, Bucket=self.bucket_name, Key=item_path)
        LOGGER.info('Upload succeeded for bucket: %s, item: %s' % (self.bucket_name, item_path))

    def download_item_from_folder(self, item_id, folder):
        item = None
        item_path = os.path.join(folder, item_id)
        item_file = self.s3_client.get_object(Bucket=self.bucket_name, Key=item_path)
        if item_file:
            item = item_file['Body'].read()
        return item
