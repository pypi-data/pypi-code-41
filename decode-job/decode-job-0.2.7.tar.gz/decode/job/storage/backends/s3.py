import boto3
import logging
import io
import os
from ..storage import Storage


class S3StorageBackend(Storage):
    def __init__(self, logger=None):
        self.client = boto3.resource('s3')
        self.logger = logger if logger else logging.getLogger("S3")

    def get_bucket(self, bucket_name):
        return self.client.Bucket(name=bucket_name)

    def delete(self, filepath, bucket_name=None):
        try:
            self.client.Object(bucket_name, filepath).delete()
            self.logger.info(
                f"Successfully deleted file {filepath} from {bucket_name}")
            return True, None
        except Exception as e:
            self.logger.error(f"Cannot delete {filepath} from {bucket_name}." +
                              f" Unexpected exception: {str(e)}")
            return False, e

    def read(self, filepath, bucket_name=None):
        bucket = self.get_bucket(bucket_name)
        bytes_buffer = io.BytesIO()
        try:
            bucket.download_file_obj(filepath, bytes_buffer)
            bytes_buffer.close()
            byte_value = bytes_buffer.getvalue()
            content = byte_value.decode()
            self.logger.info(
                f"Successfully got the content of {filepath} to {bucket_name}")
            return True, content
        except Exception as e:
            self.logger.error(f"Cannot read {filepath} from {bucket_name}." +
                              f" Unexpected exception: {str(e)}")
            return False, e

    def save_file(self, filename, key=None, bucket_name=None):
        bucket = self.get_bucket(bucket_name)
        try:
            bucket.upload_file(Filename=filename, Key=key if key else filename)
            self.logger.info(f"Successfully uploaded to {bucket_name}")
            return True, None
        except Exception as e:
            self.logger.error(f"Cannot upload to {bucket_name}." +
                              f" Unexpected exception: {str(e)}")
            return False, e

    def save(self, filename, content, bucket_name=None):
        import uuid
        random_filename = str(uuid.uuid4())
        content = content.encode("utf-8")
        with open(random_filename, "wb") as f:
            f.write(content)
        self.save_file(random_filename, filename, bucket_name=bucket_name)
        os.remove(random_filename)
