import os
import logging as log
from minio import Minio
from tqdm import tqdm
from DatastoreClient.utils import get_filename, compute_md5, get_fileszie
from minio.error import (
    ResponseError,
    BucketAlreadyOwnedByYou,
    BucketAlreadyExists,
    NoSuchKey,
)
import json


class MinIOUploader:
    def __init__(
        self,
        client=None,
        auth={"access_key": "minio", "secret_key": "minio123"},
        secure=True,
    ):
        if not client:
            entrance = os.environ.get("entrance", "127.0.0.1:9001")
            self.client = Minio(
                entrance,
                access_key=auth["access_key"],
                secret_key=auth["secret_key"],
                secure=secure,
            )
        else:
            self.client = client

    def prepare_files(self, path_to_file_or_files, metadata):
        def flatten_path(path):
            files = []
            if os.path.isdir(path):
                for file_path in os.listdir(path):
                    sub_path = os.path.join(path, file_path)
                    files += flatten_path(sub_path)
            elif os.path.isfile(path):
                files.append(path)
            log.debug({"flatten_path": files})
            return files

        def prepare_(flattened_paths, metadata):
            files = []
            bar = tqdm(desc="prepare files to upload", total=len(flattened_paths))
            for path in flattened_paths:
                filename = get_filename(path)
                this_file_metadata = metadata.copy()
                this_file_metadata["filename"] = filename
                this_file_metadata["filesize"] = get_fileszie(path)
                files.append(
                    {
                        "md5": compute_md5(path),
                        "file_path": path,
                        "metadata": this_file_metadata,
                        "name": filename,
                        "bucket": this_file_metadata["bucket"],
                    }
                )
                bar.update(1)
            log.debug({"prepare_": files})
            return files

        return prepare_(flatten_path(path_to_file_or_files), metadata)

    def upload(self, files):
        success_files = []
        failed_files = []
        already_in_bucket_files = []
        bar = tqdm(desc="uploading files", total=len(files))
        for file in files:
            metadata = file["metadata"]
            file_path = file["file_path"]
            filename = metadata["filename"]
            version = file["version"]
            try:
                self.client.make_bucket(metadata["bucket"])
                log.debug("create bucket")
            except BucketAlreadyOwnedByYou as err:
                log.debug("bucket alread owned by you, now use it.")
            except BucketAlreadyExists as err:
                log.debug("bucket alread exist, now use it.")
            except ResponseError as err:
                log.error(err)
                raise err

            file["url"] = "s3://{bucket}/{object_name}/{version}".format(
                bucket=metadata["bucket"], object_name=filename, version=version
            )
            try:
                metadata_copy = metadata.copy()
                for key, value in metadata_copy.items():
                    if isinstance(value, (dict, list)):
                        metadata_copy[key] = json.dumps(metadata_copy[key])
                try:
                    self.client.get_object(
                        metadata["bucket"],
                        "{name}/{version}".format(name=filename, version=version),
                    )
                    already_in_bucket_files.append(file)
                except NoSuchKey as err:
                    self.client.fput_object(
                        metadata["bucket"],
                        "{name}/{version}".format(name=filename, version=version),
                        file_path,
                        metadata=metadata_copy,
                    )
                    success_files.append(file)
            except ResponseError as err:
                failed_files.append(file)
                log.error(err)
            bar.update(1)
        log.debug(
            {
                "already in bucket files": [
                    file["name"] for file in already_in_bucket_files
                ]
            }
        )
        log.debug({"success to upload": [file["name"] for file in success_files]})
        log.debug({"fail to upload": [file["name"] for file in failed_files]})
        return success_files, failed_files, already_in_bucket_files


if __name__ == "__main__":
    MinIOUploader(secure=False).upload("./", metadata={"bucket": "test"})
