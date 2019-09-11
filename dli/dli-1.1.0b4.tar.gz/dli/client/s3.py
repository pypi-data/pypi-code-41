import logging
import os

import warnings
import datetime
import glob
import s3fs
import concurrent
import multiprocessing

from concurrent.futures import ThreadPoolExecutor
from wrapt import ObjectProxy
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from boto3 import Session
from botocore.exceptions import ClientError
from botocore.session import get_session
from botocore.credentials import RefreshableCredentials
from urllib.parse import urlparse, ParseResult
from dli.client.exceptions import InsufficientPrivilegesException, S3FileDoesNotExist
from tqdm import tqdm

logger = logging.getLogger(__name__)
THREADS = multiprocessing.cpu_count()


class Client:
    """
    A wrapper client providing util methods for s3fs
    """

    @classmethod
    def from_dataset(cls, client, dataset_id):
        def _credentials():
            keys = client.get_s3_access_keys_for_dataset(dataset_id)
            expiry_time = (
                # expiring the token after an hour. It's conservative
                # but it should just be refreshed. TODO add expiry time
                # to the get_s3_access_keys_for_dataset endpoint
                datetime.now().replace(tzinfo=tzlocal()) + timedelta(hours=1)
            ).isoformat()

            return dict(
                access_key=keys.access_key_id,
                secret_key=keys.secret_access_key,
                token=keys.session_token,
                expiry_time=expiry_time
            )

        session_credentials = RefreshableCredentials.create_from_metadata(
            metadata=_credentials(),
            refresh_using=_credentials,
            method='NOOP'
        )

        session = get_session()
        # Extremely dirty but it seems to be the 'blessed' way of doing this.
        session._credentials = session_credentials
        return cls(Session(botocore_session=session))

    def __init__(self, boto_session):
        self.boto_session = boto_session

        self.s3_resource = self.boto_session.resource(
            's3', endpoint_url=os.environ.get('S3_URL')
        )

        self.s3_client = self.s3_resource.meta.client
        self.s3fs = s3fs.S3FileSystem()
        self.s3fs.s3 = self.s3_client

    def download_files_from_s3_path(self, s3_path, destination):
        """
        Helper function to download a file as a stream from S3
        :param s3_path, required, example: s3://bucket_name/prefix_part1/prefix_part2/file_name.txt
        :param destination, required, must be a directory, if doesn't exist, will be created
        """
        if os.path.isfile(destination):
            raise NotADirectoryError(destination)

        parse_result = urlparse(s3_path)
        bucket = parse_result.netloc
        # Removes forward slash
        path = parse_result.path.lstrip('/').rstrip('/')

        def _download(obj_summary):
            # Ignore 'folders'
            key = obj_summary['Key']
            if not key.endswith('/'):
                destinatation_path = os.path.join(destination, key)

                subfolder = os.path.dirname(destinatation_path)
                os.makedirs(subfolder, exist_ok=True)

            logger.info('Downloading File %s to %s', key, destinatation_path)
            self.s3_client.download_file(bucket, key, destinatation_path)

        keys = list(self._list_objects(bucket, path))
        threads = max(THREADS, len(keys))
        with ThreadPoolExecutor(max_workers=threads) as executor:
            list(executor.map(_download, keys))

    def upload_files_to_s3(self, files, s3_location, token_refresher=None, num_retries=None):
        """
        Upload multiple files to a specified s3 location. The basename of the
        `files` will be preserved.

        :param List files: An list of filepaths
        :param str s3_location: Path to destination directory in S3, file will be
                 stored under <s3_location><filename>
        :param token_refresher: Optional Function to refresh S3 token *deprecated*
        :param int num_retries: Optional Number of retries in case of upload failure *deprecated*
        :returns: List of path to the files in S3
        :rtype: List[str]
        """
        if token_refresher:
            warnings.warn(
                'Credentials are now automatically refreshed.'
                'This will be removed in the next major release.',
                DeprecationWarning,
            )

        if num_retries:
            warnings.warn(
                'Retries are handled by boto.'
                'This will be removed in the next major release.',
                DeprecationWarning,
            )


        bucket_name, *prefix = s3_location.partition('/')
        bucket = self.s3_resource.Bucket(bucket_name)
        prefix = ''.join(prefix)


        def upload(file, s3_location):
            file_path = file['file']
            s3_suffix = file['s3_suffix']
            target = os.path.join(prefix, s3_suffix)

            logger.info("Uploading %s to %s", file_path, target)

            try:
                self.s3_client.upload_file(
                    file_path, bucket.name, target.lstrip('/')
                )
            except ClientError as e:
                if e.response['Error']['Code'] == 'AccessDenied':
                    raise InsufficientPrivilegesException() from e

                raise e

            logger.info(".. %s uploaded successfully.", file_path)

            return {
                "path": ParseResult(
                    scheme='s3',
                    netloc=bucket_name,
                    path=target,
                    params='', query='', fragment=''
                ).geturl(),
                "size": os.path.getsize(file_path)
            }

        files_to_upload = self._files_to_upload_flattened(files)
        result = []
        for file in files_to_upload:
            uploaded = upload(file, s3_location)

            result.append(uploaded)

        return result

    @staticmethod
    def _files_to_upload_flattened(files):
        files_to_upload = []

        for file in files:
            if not os.path.exists(file):
                raise Exception('File / directory specified (%s) for upload does not exist.' % file)

            if os.path.isfile(file):
                logger.info("detected file: %s", file)
                files_to_upload.append({'file': file, 's3_suffix': os.path.basename(file)})
            elif os.path.isdir(file):
                logger.info("detected directory: %s", file)
                all_contents = glob.glob(os.path.join(file, "**/*"), recursive=True)
                fs = [f for f in all_contents if os.path.isfile(f)]

                for f in fs:
                    files_to_upload.append({'file': f, 's3_suffix': os.path.relpath(f, file)})

        return files_to_upload

    def _list_objects(self, bucket, prefix):
        # as it turns out the high level boto client is rather expensive
        # when creating objects en mess. This is at least 50% faster.
        # This is also the exact way that the aws cli lists files.
        paginator = self.s3_client.get_paginator(
            'list_objects_v2'
        )

        paging_args = {'Bucket': bucket, 'Prefix': prefix}
        iterator = paginator.paginate(**paging_args)

        for response_data in iterator:
            for obj in response_data.get('Contents'):
                yield obj


class File(ObjectProxy):
    """
    This is only to mantain backwards compatibility with S3FS.
    Ideally we want to deprecate getting files as anything but
    context managers. This provides both the context manageer
    and function that returns a files like object
    """
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.__wrapped__.close()


class S3DatafileWrapper:
    def __init__(self, datafile, client):
        # we want to override the files property
        # it isn't really needed for py3 but it is in py2
        self.__dict__ = {
            k: v for k,v in datafile.items() if k != "files"
        }
        self._datafile = datafile
        self._client = client

    def __getitem__(self, path):
        """
        :param str path: The path of the file to retrieve from s3.
        :returns: A S3File instance
        """
        return self.open_file(path)

    def open_file(self, path):
        """
        Helper method to load an specific file inside a datafile
        without having to download all of it.

        :param str path: The path of the file to retrieve from s3.
        :returns: A S3File instance that can be used as a normal python file
        """
        bucket, _, key = path.partition('/')

        try:
            bucket = self._client.s3_resource.Bucket(bucket)
            response = bucket.Object(key).get()['Body']
            return File(response)
        except (
            self._client.s3_resource.meta.client.exceptions.NoSuchKey,
            self._client.s3_resource.meta.client.exceptions.NoSuchBucket
        ) as e:
            raise S3FileDoesNotExist(path)

    def __repr__(self):
        return str(dict(self._datafile))

    @property
    def files(self):
        """
        Lists all S3 files in this datafile, recursing on folders (if any)
        """
        files = self._datafile["files"]
        if not files:
            return []

        bucket = urlparse(files[0]['path']).netloc

        prefix = os.path.commonprefix([
            urlparse(file_['path']).path for file_ in files
        ]).lstrip('/')

        return [
            '{}/{}'.format(bucket, obj['Key']) for obj in
            self._client._list_objects(bucket, prefix)
        ]
