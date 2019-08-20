import re
import os
from DatastoreClient.utils import check_protoype
from minio import Minio
from minio.error import (
    ResponseError,
    BucketAlreadyOwnedByYou,
    BucketAlreadyExists,
    NoSuchKey,
)
from tqdm import tqdm


class MinIODownloader:
    def __init__(
        self,
        client=None,
        secure=True,
        download_path="/home/vol/",
        write_chunk_size=1024 * 3,
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

        self.download_path = download_path
        if not os.path.exists(self.download_path):
            os.mkdir(self.download_path)
            # TODO: Need Recursive Creation here.
        self.write_chunk_size = write_chunk_size

    def local_file_path(self, filename):
        file_path = os.path.join(self.download_path, filename)
        return file_path

    def is_cached(self, file_path):
        return os.path.exists(file_path)

    def _download(self, resource):
        file_path = self.local_file_path(resource["name"])
        if not self.is_cached(file_path):
            try:
                url = resource["url"]
                pattern = re.compile(r"s3:\/\/(.*?)\/(.*?)$")
                res = pattern.findall(url)
                if res:
                    bucket, object_name = res[0]
                    data = self.client.get_object(bucket, object_name)
                    with open(file_path, "wb") as file_data:
                        for d in data.stream(self.write_chunk_size):
                            file_data.write(d)
                    return file_path
                else:
                    raise Exception("can not parse this url!")

            except NoSuchKey as err:
                print(err)
            except ResponseError as err:
                print(err)
        else:
            print("use cache")

    def download(self, resources):

        filepaths = []
        prototype = {
            "name": "filename",
            "url": "where I can download the file, which is a custom s3 link, looks like: s3://<bucket>/<name>:<version>",
        }
        bar = tqdm(desc="download files", total=len(resources))
        for resource in resources:
            # TODO: Need Multiple Threading Download Here.
            if check_protoype(prototype, resource):
                filepaths.append(self._download(resource))
            bar.update(1)
        return filepaths
