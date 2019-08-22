import os
import re

import boto3
import mimetypes

from hashlib import md5
from time import localtime


class S3Service(object):
    data_uri_pat = r'^data:(?P<content_type>[A-Za-z\/\-\+.]*);base64,(?P<bytes>.*)$'    

    def __init__(self,
            region_name,
            endpoint_url,
            aws_access_key_id,
            aws_secret_access_key):
        self.description = 'Amazon S3 or Amazon Simple Storage Service is\
a "simple storage service" offered by Amazon Web Services that provides object storage through a web service interface.'
        self.conn = boto3.resource('s3',
                        region_name=region_name,
                        endpoint_url=endpoint_url,
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key)

    def _upload_file_to_cloud(self,
            media_location,
            file_key,
            bucket,
            mime,
            guess_mime,
            acl):
        buck = self.conn.Bucket(bucket)
        if type(file) == FileStorage:
            body = open(media_location, 'rb')
        else:
            body = file

        params = dict(
            Key=file_key,
            Body=body,
            ACL=acl)
        if mime:
            params['ContentType'] = mime
        elif guess_mime:
            guess_mime = mimetypes.guess_type(media_location)[0]
            if guess_mime:
                params['ContentType'] = guess_mime

        buck.put_object(**params)
        return '{}/{}/{}'.format(self.base_url, bucket, file_key)


    def is_data_uri(file):
        return bool(re.match(data_uri_pat, file))

    def get_file_bytes(data_uri):
        return re.match(data_uri_pat, data_uri)

    def _save_file_to_local(self,
            file,
            filename):
        media_location = '{}/{}'.format(os.getcwd(), filename)
        file.save(media_location)
        return media_location


    def _remove_file_from_local(self,
            media_location):
        os.remove(media_location)


    def _get_filename(self, file):
        *_, filename =  file.filename.split('/')
        return filename


    def _get_random_filename(self):
        return md5(str(localtime()).encode('utf-8')).hexdigest()

    def upload_file(self,
            file,
            bucket,
            folder='',
            filename=None,
            mime=None,
            guess_mime=False,
            acl='private'):
        if type(file) == FileStorage:
            filename = self._get_filename(file)
        elif type(file) == str and is_data_uri(file):
            mime, file_bytes = self.get_file_bytes(file)
            filename = self._get_random_filename()
        else:
            raise ValueError('Invalid file provided')

        if not filename:
            if type(file) == FileStorage:
                filename = self._get_filename(file)
            else:
                filename = self._get_random_filename()

        file_key = filename
        if folder:
            file_key = '{}/{}'.format(folder, filename)
        media_location = self._save_file_to_local(file, filename)
        file_url = self._upload_file_to_cloud(
            media_location,
            file_key,
            bucket,
            mime,
            guess_mime,
            acl
        )
        self._remove_file_from_local(media_location)
        return file_url
