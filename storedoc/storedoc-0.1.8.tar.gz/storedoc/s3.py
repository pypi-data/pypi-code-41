import os
import re

import boto3
import urllib
import mimetypes

from hashlib import md5
from time import localtime

from werkzeug.datastructures import FileStorage 


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
            file,
            file_key,
            bucket,
            mime,
            guess_mime,
            acl):
        buck = self.conn.Bucket(bucket)
        params = dict(
            Key=file_key,
            Body=file,
            ACL=acl)
        if mime:
            params['ContentType'] = mime
        elif guess_mime:
            guess_mime = mimetypes.guess_type(file_key)[0]
            if guess_mime:
                params['ContentType'] = guess_mime

        buck.put_object(**params)
        return '{}/{}/{}'.format(self.base_url, bucket, file_key)


    def _is_data_uri(self, file):
        return bool(re.match(self.data_uri_pat, file))

    def _get_file_bytes(self, data_uri):
        match = re.match(self.data_uri_pat, data_uri)
        if match:
            return match.groups()
        raise ValueError('Invalid file provided')

    def _get_filename(self, file):
        *_, filename =  file.filename.split('/')
        return filename

    def _get_random_filename(self, content_type):
        ext = mimetypes.guess_extension(content_type)
        filename = '{}{}'.format(
                md5(str(localtime()).encode('utf-8')).hexdigest(),
                ext
            )
        return filename

    def upload_file(self,
            file,
            bucket,
            folder='',
            filename=None,
            mime=None,
            guess_mime=False,
            acl='private'):
        if type(file) == FileStorage:
            _filename = self._get_filename(file)
        elif type(file) == str and self._is_data_uri(file):
            mime, file_bytes = self._get_file_bytes(file)
            _filename = self._get_random_filename(mime)
            response = urllib.request.urlopen(file)
            file = response.file.read()
        else:
            raise ValueError('Invalid file provided')

        filename = filename if filename else _filename
        file_key = filename
        if folder:
            file_key = '{}/{}'.format(folder, filename)

        file_url = self._upload_file_to_cloud(
            file,
            file_key,
            bucket,
            mime,
            guess_mime,
            acl
        )
        return file_url
