import os
from datetime import datetime, timedelta
from pathlib import Path

from azure.storage.blob import BlockBlobService, BlobPermissions

from .exceptions import NoBlobsFound

__all__ = ['AzureBlobDownload']


class AzureBlobDownload:
    """
    Download a file or folder.
    """

    def __init__(self, account_name: str, account_key: str, container_name: str):
        """
        :param account_name:
            Azure storage account name.
        :param account_key:
            Azure storage key.
        :param container_name:
            Azure storage container name, URL will be added automatically.
        """
        self.account_name = account_name
        self.account_key = account_key
        self.container_name = container_name

        self.block_blob_service = BlockBlobService(self.account_name, self.account_key)

    def download_file(self, blob_name: str, download_to: str = None):
        """
        Download a file to a location.

        :param blob_name:
            Give a blob path with file name.
        :param download_to:
            Give a local absolute path to download.
        :raises OSError: If the directory for ``download_to`` does not exists

        >>> from azblobexplorer import AzureBlobDownload
        >>> az = AzureBlobDownload('account name', 'account key', 'container name')
        >>> az.download_file('some/name/file.txt')
        """

        file_dict = self.read_file(blob_name)
        file_name = Path(file_dict['file_name']).name

        if download_to is None:
            write_to = file_name
        else:
            write_to = Path(os.path.join(download_to, file_name))
            write_to.parent.mkdir(parents=True, exist_ok=True)

        with open(write_to, 'wb') as file:
            file.write(file_dict['content'])

    def download_folder(self, blob_folder_name: str, download_to: str = None):
        """
        Download a blob folder.

        :param blob_folder_name:
            Give a folder name.
        :param download_to:
            Give a local path to download.
        :raises NoBlobsFound: If the blob folder is empty or is not found.
        :raises OSError: If the directory for ``download_to`` does not exists

        >>> from azblobexplorer import AzureBlobDownload
        >>> az = AzureBlobDownload('account name', 'account key', 'container name')
        >>> az.download_folder('some/name/file.txt')
        """

        blobs = self.block_blob_service.list_blobs(self.container_name, blob_folder_name)

        if blobs.items == 0:
            raise NoBlobsFound(
                "There where 0 blobs found with blob path '{}'".format(blob_folder_name))

        if download_to is None:
            for blob in blobs:
                name = blob.name
                path = Path(os.path.join(blob_folder_name, name))
                path.parent.mkdir(parents=True, exist_ok=True)
                _blob = self.read_file(name)
                file = open(path, 'wb')
                file.write(_blob['content'])
                file.close()
        else:
            for blob in blobs:
                name = blob.name
                path = Path(os.path.join(download_to, blob_folder_name, name))
                path.parent.mkdir(parents=True, exist_ok=True)
                _blob = self.read_file(name)
                file = open(path, 'wb')
                file.write(_blob['content'])
                file.close()

    def read_file(self, blob_name: str) -> dict:
        """
        Read a file.

        :param blob_name:
            Give a file name.
        :return:
            Returns a dictionary of name, content,

        >>> from azblobexplorer import AzureBlobDownload
        >>> az = AzureBlobDownload('account name', 'account key', 'container name')
        >>> az.read_file('some/name/file.txt')
        {
            'file_name': 'file.txt',
            'content': byte content,
            'file_size_bytes': size in bytes
        }
        """

        blob_obj = self.block_blob_service.get_blob_to_bytes(self.container_name, blob_name)

        return {
            'file_name': blob_obj.name,
            'content': blob_obj.content,
            'file_size_bytes': blob_obj.properties.content_length
        }

    def generate_url(self, blob_name: str, permission: BlobPermissions = BlobPermissions.READ, sas: bool = False) -> str:
        """
        Generate's blob URL. It can also generate Shared Access Signature (SAS) if ``sas=True``.

        :param blob_name: Name of the blob
        :type blob_name: str
        :param permission: Permissions for the data
        :type permission: azure.storage.blob.BlobPermissions
        :param sas: Set ``True`` to generate SAS key
        :type sas: bool
        :return: Blob URL
        :rtype: str
        """

        if sas:
            token = self.block_blob_service.generate_blob_shared_access_signature(
                self.container_name,
                blob_name,
                permission=permission,
                expiry=datetime.utcnow() + timedelta(hours=1)
            )
            return self.block_blob_service.make_blob_url(self.container_name, blob_name, sas_token=token)
        else:
            return self.block_blob_service.make_blob_url(self.container_name, blob_name)

    def generate_url_mime(self, blob_name: str, mime_type: str, sas: bool = False,
                          permission: BlobPermissions = BlobPermissions.READ) -> str:
        """
        Generate's blob URL with MIME type. It can also generate Shared Access Signature (SAS) if ``sas=True``.

        :param blob_name: Name of the blob
        :type blob_name: str
        :param mime_type: MIME type of the application
        :type mime_type: str
        :param sas: Set ``True`` to generate SAS key
        :type sas: bool
        :param permission: Permissions for the data
        :type permission: azure.storage.blob.BlobPermissions
        :return: Blob URL
        :rtype: str
        """

        if sas:
            token = self.block_blob_service.generate_blob_shared_access_signature(
                self.container_name,
                blob_name,
                permission=permission,
                expiry=datetime.utcnow() + timedelta(hours=1),
                content_type=mime_type
            )
            return self.block_blob_service.make_blob_url(self.container_name, blob_name, sas_token=token)
        else:
            return self.block_blob_service.make_blob_url(self.container_name, blob_name)
