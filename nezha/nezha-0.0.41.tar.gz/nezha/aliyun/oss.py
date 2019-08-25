import oss2
from oss2 import Bucket

class OSS(object):
    """
    aliyun oss sdk
    """

    def __init__(self, access_key_id: str, access_key_secret: str, bucket_name: str, endpoint: str):
        self.bucket: Bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
        self.get_file_expires: int = 3600 * 24

    def get(self, file_path: str) -> str:
        """
        从oss获取文件的url
        :param file_path: 文件的oss存储路径
        """
        return self.bucket.sign_url('GET', file_path, self.get_file_expires)

    def upload(self, file_path: str, file: str) -> bool:
        """
        上传文件到oss
        :param file_path: 文件的oss存储路径
        :param file: 上传文件
        :return: 上传状态
        """
        result = self.bucket.put_object(key=file_path, data=file)
        if result.status == 200:
            return True
        else:
            return False
