import os
from pathlib import Path

from azure.storage.blob import BlockBlobService

__all__ = ['AzureBlobUpload']


class AzureBlobUpload:
    """
    Upload a file or a folder.
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

    def upload_file(self, file_path: str, upload_to: str = None):
        """
        Upload a file to a given blob path.

        :param upload_to:
            Give the path to upload.
        :param file_path:
            Absolute path of the file to upload.

        >>> from azblobexplorer import AzureBlobUpload
        >>> import os
        >>> az = AzureBlobUpload('account name', 'account key', 'container name')
        >>> here = os.path.abspath(os.path.dirname(__file__)) + os.sep
        >>> az.upload_file(os.path.join(here, 'file1.txt'), 'blob_folder/')
        """

        path = Path(file_path)

        if upload_to is None:
            self.block_blob_service.create_blob_from_path(self.container_name, path.name, path)
        else:
            self.block_blob_service.create_blob_from_path(self.container_name,
                                                          upload_to + path.name, path)

    def upload_files(self, files_path: list):
        """
        Upload a list of files.

        :param list files_path:
            A list of files to upload.

        >>> import os
        >>> from azblobexplorer import AzureBlobUpload
        >>> az = AzureBlobUpload('account name', 'account key', 'container name')
        >>> here = os.path.abspath(os.path.dirname(__file__)) + os.sep
        >>> path_list = [
        ...     [os.path.join(here, 'file1.txt'), 'folder_1/'],
        ...     [os.path.join(here, 'file2.txt'), 'folder_2/'],
        ...     os.path.join(here, 'file3.txt')
        ... ]
        >>> az.upload_files(path_list)
        """

        for path in files_path:
            if isinstance(path, list):
                self.upload_file(path[0], path[1])
            else:
                self.upload_file(path)

    def upload_folder(self, folder_path: str, upload_to: str = None):
        """
        Upload a folder to a given blob path.

        :param upload_to:
            Give the path to upload. Default ``None``.
        :param folder_path:
            Absolute path of the folder to upload.

        **Example without "upload_to"**

        >>> import os
        >>> from azblobexplorer import AzureBlobUpload
        >>> here = os.path.abspath(os.path.dirname(__file__)) + os.sep
        >>> az = AzureBlobUpload('account name', 'account key', 'container name')
        >>> az.upload_folder(os.path.join(here, 'folder_name'))

        **Example with "upload_to"**

        >>> import os
        >>> from azblobexplorer import AzureBlobUpload
        >>> here = os.path.abspath(os.path.dirname(__file__)) + os.sep
        >>> az = AzureBlobUpload('account name', 'account key', 'container name')
        >>> az.upload_folder(os.path.join(here, 'folder_name'), upload_to="my/blob/location/")
        """

        path = Path(folder_path)

        if not path.is_dir():
            raise TypeError("The path should be a folder.")

        root_name = path.name

        for _dir, _, files in os.walk(path):
            for file_name in files:
                rel_dir = os.path.relpath(_dir, path)
                rel_folder_path = os.path.join(root_name, rel_dir) + '/'
                abs_path = os.path.join(_dir, file_name)
                if upload_to is None:
                    self.upload_file(abs_path, rel_folder_path)
                else:
                    self.upload_file(abs_path, upload_to + rel_folder_path)
