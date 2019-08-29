# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Blob info of Open Image Dataset."""


class OpenImageBlobInfo:
    """Blob info of Open Image Datatset."""

    def __init__(self):
        """Initialize Blob Info."""

        self.blob_account_name = "openimagestorage" 
        self.blob_container_name = "openimagedataset"
        self.blob_sas_token = (
            r"?st=2019-07-31T09%3A27%3A58Z&se=2119-08-01T09%3A27%3A00Z&sp=rl&sv=2018-03-28&sr=c"
            # [SuppressMessage("Microsoft.Security", "CS002:SecretInNextLine", Justification="Offline sas token")]
            r"&sig=CQr92AvZjItFDYC4S3ZbE%2Bsj%2F%2BD2W9AmPfKwgb8Dr7E%3D")

        self.table_bbox_path = "/datasetTable/bbox.csv"
        self.table_category_path = "/datasetTable/category.csv"
        self.table_imageInfo_path = "/datasetTable/image-t1.csv"
        self.table_imageBoxNum_path = "/datasetTable/image-t2.csv"
        self.table_imageUrl_path = "/datasetTable/image-t3.csv"
        self.azcopy_win_path = "/AzCopy/azcopy.exe"
        self.azcopy_linux_path = "/AzCopy/azcopy"
        self.url_prefix = "https://openimagestorage.blob.core.windows.net/openimagedataset/"
        