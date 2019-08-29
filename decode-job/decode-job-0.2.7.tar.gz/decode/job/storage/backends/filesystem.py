import os
import logging
import io

from ..storage import Storage


class FilesystemBackend(Storage):
    def __init__(self, logger=None):
        self.logger = logger if logger else logging.getLogger("S3")

    def delete(self, filepath, bucket_name=None):
        try:
            os.remove(filepath)
            return True, None
        except Exception as e:
            self.logger.error(f"Cannot delete {filepath}." +
                              f" Unexpected exception: {str(e)}")
            return False, e

    def read(self, filepath, bucket_name=None):
        try:
            content_file = open(filepath, "r")
            content = content_file.read()
            content_file.close()
            return True, content
        except Exception as e:
            self.logger.error(f"Cannot read {filepath}." +
                              f" Unexpected exception: {str(e)}")
            return False, e

    def save_file(self, filename, bucket_name):
        return True, None

    def save(self, filename, content, bucket_name=None):
        try:
            content_file = open(filename, "w+")
            content_file.write(content)
            content_file.close()
            return True, None
        except Exception as e:
            self.logger.error(f"Cannot save {filename}." +
                              f" Unexpected exception: {str(e)}")
            return False, e
