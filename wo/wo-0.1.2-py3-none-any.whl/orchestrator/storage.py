from wo.cloud.aws import S3
from wo.cloud.gcp import GoogleStorage
import urllib.parse, logging, sys, os

__all__ = ["Storage"]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Storage:

    def _parse_uri(self, uri):
        """
        Parse given URI into subparts.

        Parameters
        ----–-----
        uri: str
            URI, containing scheme, bucket name and possibly path, pointing to a file/folder.
        
        Returns
        -------
        tuple: (scheme, bucket_name, key)
            A tuple, which contains bucket scheme (either s3 or gs), a bucket name 
            and key/prefix representing relative path in the bucket.
        """
        result = urllib.parse.urlparse(uri)
        if not result.scheme:
            raise ValueError("URI must contain scheme and a bucket name")
        if result.scheme not in ('s3', 'gs'):
            raise ValueError("Only s3 and gs are supported")
        return result.scheme, result.netloc, result.path.strip("/")
    
    def _parse_key(self, uri):
        """
        Parse given URI and retrieve relative path.

        Parameters
        ----------
        uri: str
            URI, containing scheme, bucket name and possibly path, pointing to a file/folder.
        
        Returns
        -------
        str
            Key/relative path, retrieved from URI, pointing to some file/folder.
        """
        return urllib.parse.urlparse(uri).path.strip("/")

    def upload_file(self, source_path, destination_path, cache=True):
        assert os.path.isfile(source_path), "{} must be file".format(source_path)
        scheme, bucket, key = self._parse_uri(destination_path)
        logger.info("Uploading file {} to {}".format(source_path, destination_path))

        if scheme == "s3":
            return S3._upload_file_s3(bucket, source_path, key, cache=cache)
        if scheme == 'gs': 
            return GoogleStorage._upload_file_gs(bucket, source_path, key, cache=cache)

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
        scheme, bucket, key = self._parse_uri(source_path)
        relative_destination_path = self._parse_key(destination_path)
        logger.info("Downloading file {} to {}".format(source_path, relative_destination_path))

        dirname = os.path.dirname(relative_destination_path)
        if dirname: os.makedirs(dirname, exist_ok=True)
        if scheme == "s3": 
            return S3._download_file_s3(bucket, key, relative_destination_path, cache=cache)
        if scheme == "gs": 
            return GoogleStorage._download_file_gs(bucket, key, relative_destination_path, cache=cache)

    def download_prefix(self, source_prefix, destination_prefix, cache=True):
        logger.info("Downloading prefix {} to {}".format(source_prefix, destination_prefix))

        for fullpath, relpath in self.list_prefix(source_prefix):
            download_path = self._parse_key(destination_prefix)
            relative_download_path = os.path.join(download_path, relpath)
            dirname = os.path.dirname(relative_download_path)
            if dirname: os.makedirs(dirname, exist_ok=True)
            self.download_file(fullpath, relative_download_path, cache=cache)

    def list_prefix(self, source_prefix):
        scheme, bucket, key = self._parse_uri(source_prefix)
        logger.info("Listing files from {}".format(source_prefix))

        if scheme == 's3': 
            return iter(S3._list_folder_s3(bucket, key))
        if scheme == 'gs': 
            return iter(GoogleStorage._list_folder_gs(bucket, key))