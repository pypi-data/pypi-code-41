import logging, sys, os
from google.cloud import storage
from wo.utils import io

__all__ = ["GoogleStorage"]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class GoogleStorage: 

    @staticmethod
    def _download_file_gs(bucket, source_path, destination_path, **kwargs):
        """
        Download file from bucket.

        Parameters
        ----------
        source_path: str
            Relative path in the bucket, where file is located.
        destination_path: str
            Path, where file should be downloaded.
        bucket: str
            Bucket name, where file is located.
        """
        storage.Client().get_bucket(bucket).blob(source_path).download_to_filename(destination_path)

    @staticmethod
    def _upload_file_gs(bucket, source_path, destination_path, **kwargs):
        """
        Upload file to bucket. 

        Parameters
        ----------
        source_path: str
            Path to target file, which have to be uploaded.
        destination_path: str
            Relative path in the bucket, where file should be uploaded. 
        bucket: str
            Bucket name, where file has to be uploaded.
        """
        storage.Client().get_bucket(bucket.name).blob(destination_path).upload_from_filename(source_path)

    @staticmethod
    def _list_folder_gs(bucket, source_folder, **kwargs): 
        """
        List all files in the bucket under a specified path. 

        Parameters
        ----------
        source_folder: str
            Path, from which to look up folder down the tree.
        bucket: str
            Bucket name, where to look up files.
        
        Returns
        -------
        iter: (full_path, relative_path)
            Returns an iterator, which produces a tuple of full s3 uri to the file and
            a relative path from a given prefix `source_folder`.
        """
        for blob in storage.Client().get_bucket(bucket.name).list_blobs(prefix=source_folder):
            yield '/'.join(("gc:/", bucket, blob.strip('/'))), \
                os.path.relpath(blob.name, source_folder) 