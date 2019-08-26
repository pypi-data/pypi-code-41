import logging, sys, os
import boto3 
from wo.utils import io

__all__ = ["S3"]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class S3: 

    @staticmethod
    def _download_file_s3(bucket, source_path, destination_path, cache=True):
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
        cache: bool
            If file already persists locally, skip downloading if md5 checksums are similar. 
        """
        s3 = boto3.resource('s3')

        if os.path.exists(destination_path) and cache:
            head = s3.meta.client.head_object(Bucket=bucket, Key=source_path)
            if head.get("Metadata", {}).get("md5") == io.md5_file(destination_path):
                return logger.debug("Local and remote objects are the same, skipping download")

        s3.Object(bucket, source_path).download_file(destination_path)

    @staticmethod
    def _upload_file_s3(bucket, source_path, destination_path, cache=True):
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
        cache: bool
            If file already exists, upload file only when md5 checksums are different. 
        """
        s3 = boto3.resource('s3')

        if cache:
            try:
                head = s3.meta.client.head_object(Bucket=bucket, Key=destination_path)
                if head.get("Metadata", {}).get("md5") == io.md5_file(source_path):
                    return logger.debug("Local and remote objects are the same, skipping upload")
            except boto3.exceptions.botocore.exceptions.ClientError as e:
                logger.debug(e)
            
        s3.meta.client.upload_file(
            Filename=source_path, 
            Bucket=bucket, 
            Key=destination_path, 
            ExtraArgs={
                "Metadata": {
                    "md5": io.md5_file(source_path)
                }, 
            },
        )

    @staticmethod
    def _list_folder_s3(bucket, source_folder):
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

        Raises
        ------
        ValueError
            If in the given 
        """

        s3 = boto3.resource('s3')
        result = s3.meta.client.list_objects_v2(Bucket=bucket, Prefix=source_folder)

        if result["IsTruncated"]: 
            logger.warning("Result of the files look up will be truncated to 1000 objects.")
        if not result.get("Contents"):
            raise ValueError("Could not find any contents under a specified folder")

        for path in result["Contents"]:
            yield '/'.join(("s3:/", bucket, path["Key"].strip('/'))), \
                os.path.relpath(path["Key"], source_folder)
