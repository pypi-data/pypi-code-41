import os
import base64
from collections import OrderedDict
from minio import Minio
from graphqlclient import GraphQLClient
from DatastoreClient.Resources import *
from DatastoreClient.Structures import *
from DatastoreClient.Queryer import *
from DatastoreClient.Uploader import *
from DatastoreClient.Downloader import *
import pkg_resources
import logging as log


class Client:
    """
        客户端，提供了对MinIO的操作封装
        结合Uploader和Downloader使用，可以简化MinIO客户端操作逻辑
    """

    def __init__(
        self,
        auth={"access_key": "minio", "secret_key": "minio123"},
        graphql_entrance=os.environ.get("entrance", "127.0.0.1"),
        minio_entrance=os.environ.get("entrance", "127.0.0.1"),
        minio_secure=True,
        graphql_path="/graphql/",
        download_path="/home/vol",
    ):

        minio_url = "{entrance}".format(entrance=minio_entrance)
        graphql_url = "{entrance}/{path}".format(
            entrance=graphql_entrance, path=graphql_path
        )

        self.minioClient = Minio(
            minio_url,
            access_key=auth["access_key"],
            secret_key=auth["secret_key"],
            secure=minio_secure,
        )

        self.uploader = MinIOUploader(client=self.minioClient)
        self.downloader = MinIODownloader(
            client=self.minioClient, download_path=download_path
        )
        self.graphqlClient = GraphQLClient(graphql_url)
        self.queryer = GraphQLQueryer(client=self.graphqlClient)
        path = "graphqls/"
        graphqls = pkg_resources.resource_filename(__name__, path)
        self.queryer.generate_query_funcs(graphqls)

        self.model = Model(queryer=self.queryer, uploader=self.uploader)
        self.weight = Weight(queryer=self.queryer, uploader=self.uploader)
        self.raw = Raw(queryer=self.queryer, uploader=self.uploader)
        self.attachment = Attachment(queryer=self.queryer, uploader=self.uploader)

        self.dataset = DataSet(queryer=self.queryer)


if __name__ == "__main__":
    # test code
    # this test code shows that:
    #   crate a lot of raw datas
    #   upload them to datastore
    #   gather them togher to create a dataset name 'L-in-H'
    #   and query them out in tow style
    log.getLogger().setLevel(log.INFO)

    # DataStore Client, next coming: DataStore Command Line Tools
    client = Client(
        graphql_entrance="http://127.0.0.1:30000",
        minio_entrance="127.0.0.1:30000",
        graphql_path="graphql/v1/graphql",
        minio_secure=False,
        download_path="./test_data",
    )

    for i in range(20):
        with open("./test_data/test{}.txt".format(i), "w+") as f:
            import random

            f.write(str("hi"))

    raws = client.raw.create(
        "./test_data/",
        metadata={
            "bucket": "raws",  # the name of the bucket
            "source": "tell me more detail where this object come from!",
            "class_tree": {
                "big_image": "HSIL",
                "cell": "LSIL",
                "instance": "independent",
            },
            "hi": "this is a test, you can add any key you want",
            "but": "every resources has a prototype keys that you must contains",
        },
    )

    err, dataset = client.dataset.create(
        name="L-in-H",
        metadata={
            "note": "this dataset contains all the LSIL cell from HSIL big image"
        },
    )

    err, dataset_with_raws = client.dataset.add_raws(dataset=dataset, resources=raws)

    err, raws = client.raw.query(
        """
        {
            dataset_id: {
                _eq: 1
            }
        }
        """
    )

    err, res = client.queryer.query(
        """
        {
          data_raw(where: {metadata: {_contains: {class_tree: {cell: "LSIL"}}}, tag: {_eq: "latest"}}, distinct_on: id) {
            id
            metadata
            tag
            version
            url
            name
          }
        }
        """
    )
    raws = res["data"]["data_raw"]
    print(client.downloader.download(raws))

    for i in range(20):
        os.remove("test_data/test{}.txt".format(i))
