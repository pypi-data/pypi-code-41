from wo.utils import io
from wo.cloud.aws import S3
from wo.cloud.gcp import GoogleStorage
import urllib.parse, logging, sys, os

__all__ = ["Storage"]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Storage:

    def upload_file(self, source_path, destination_path, cache=True):
        assert os.path.isfile(source_path), "{} must be file".format(source_path)
        scheme, bucket, key = io.parse_uri(destination_path)
        logger.info("Uploading file {} to {}".format(source_path, destination_path))

        if scheme == "s3":
            return S3.upload_file(bucket, source_path, key, cache=cache)
        if scheme == 'gs': 
            return GoogleStorage.upload_file(bucket, source_path, key, cache=cache)

    def upload_prefix(self, source_prefix, destination_prefix, cache=True):
        """
        Upload all files inside source_prefix to destination_prefix.

        Parameters
        ----------
        source_prefix: str
        destination_prefix: str 
        cache=True: bool
        """
        assert os.path.isdir(source_prefix), "{} must be directory".format(source_prefix)
        logger.info("Uploading prefix {} to {}".format(source_prefix, destination_prefix))

        for root, _, files in os.walk(source_prefix):
            for file in files:
                source_path = os.path.relpath(os.path.join(root, file), source_prefix)
                destination_path = os.path.join(destination_prefix, source_path)
                self.upload_file(os.path.join(root, file), destination_path, cache=cache)

    def download_file(self, source_path, destination_path, cache=True):
        scheme, bucket, key = io.parse_uri(source_path)
        relative_destination_path = io.parse_path(destination_path)
        logger.info("Downloading file {} to {}".format(source_path, relative_destination_path))

        dirname = os.path.dirname(relative_destination_path)
        if dirname: os.makedirs(dirname, exist_ok=True)
        if scheme == "s3": 
            return S3.download_file(bucket, key, relative_destination_path, cache=cache)
        if scheme == "gs": 
            return GoogleStorage.download_file(bucket, key, relative_destination_path, cache=cache)

    def download_prefix(self, source_prefix, destination_prefix, cache=True):
        logger.info("Downloading prefix {} to {}".format(source_prefix, destination_prefix))

        for fullpath, relpath in self.list_prefix(source_prefix):
            download_path = io.parse_path(destination_prefix)
            relative_download_path = os.path.join(download_path, relpath)
            dirname = os.path.dirname(relative_download_path)
            if dirname: os.makedirs(dirname, exist_ok=True)
            self.download_file(fullpath, relative_download_path, cache=cache)

    def list_prefix(self, source_prefix):
        scheme, bucket, key = io.parse_uri(source_prefix)
        logger.info("Listing files from {}".format(source_prefix))

        if scheme == 's3': 
            return iter(S3.list_folder(bucket, key))
        if scheme == 'gs': 
            return iter(GoogleStorage.list_folder(bucket, key))

    def object_exists(self, path):
        scheme, bucket, key = io.parse_uri(path)
        
        if scheme == 's3':
            return S3.object_exists(bucket, key)
        if scheme == 'gs':
            raise NotImplementedError