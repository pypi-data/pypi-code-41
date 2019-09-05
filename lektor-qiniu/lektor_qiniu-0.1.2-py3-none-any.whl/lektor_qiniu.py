# -*- coding: utf-8 -*-
from lektor.pluginsystem import Plugin
from lektor.publisher import Publisher
from qiniu import Auth, put_file, etag
import qiniu.config
from qiniu import CdnManager
import os
import inifile
from datetime import datetime 

class qiniuPublisher(Publisher):
    def get_config(self,ini_file):
        path = os.path.join(self.env.root_path,'configs',ini_file)
        return inifile.IniFile(path)

    def split_bucket_uri(self, target_url):
        bucket = target_url.netloc
        key = target_url.path
        if key != '':
            if key.startswith('/'):
                key = key[1:]
            if not key.endswith('/'):
                key = key + '/'
        return bucket, key
    
    def list_local(self):
        all_files = []
        ex_dirs = self.get_config('qiniu.ini').get('exclusions.dirs').split(',')
        ex_files = self.get_config('qiniu.ini').get('exclusions.files').split(',')
        for path, _, files in os.walk(self.output_path):
            for f in files:
                if f not in ex_files:
                    fullpath = os.path.join(path, f)
                    relpath = os.path.relpath(fullpath, self.output_path)
                    if os.path.dirname(relpath) not in ex_dirs:
                        all_files.append(os.path.relpath(fullpath, self.output_path))

        return all_files

    def publish(self, target_url, credentials=None, **extra):

        # read auth keys from config file which they name shoudl be "qiniu.ini"
        config = self.get_config('qiniu.ini')
        access_key = config.get('auth.Access_Key')
        secret_key = config.get('auth.Secret_Key')
        bucket_name, key_prefix = self.split_bucket_uri(target_url)

        # prepare local files and upload status variables
        local = self.list_local()
        qn = Auth(access_key, secret_key)
        start_time = datetime.now()
        yield "### start to upload to bucket %s %s " % (bucket_name, key_prefix)
        counter = 0
        num_files = len(local)

        ### upload files
        for filename in local:
            counter = counter+1
            abs_path = os.path.join(self.output_path, filename)
            yield '### uploading %s  ###' % filename
            key_name = key_prefix+filename
            token = qn.upload_token(bucket_name,key_name,120)
            ret,info=put_file(token,key_name,abs_path)
            if info.status_code ==200:
                yield '-- Successfully uploaded %s of %s files --' % (str(counter),num_files)
            else:
                yield 'something wrong %s' % info.status_code
                yield 'Full error message: %s' % info
        last_time = datetime.now()-start_time
        yield "$$$ Upload Done in %s seconds!" % last_time.seconds

        ##start to refresh cdn dir
        if config.get('cdn.refresh_enable') == "yes":
            yield "start to refresh"
            cdn_namager = CdnManager(qn)
            refresh_url = config.get('cdn.refresh_url')
            if refresh_url[-1]!='/':
                refresh_url = refresh_url+"/"
            dir = [refresh_url]
            refresh_dir_result = cdn_namager.refresh_dirs(dir)
            print(refresh_dir_result)
            if refresh_dir_result[0]['code'] ==200:
                yield "refresh complete!"
            else:
                yield "Error refreshing:  %s" % refresh_dir_result[0]
        yield "ALL TASK ARE COMPLETED!"

class QiniuPlugin(Plugin):
    name = 'qiniu'
    description = u'A plugin for lektor to deploy to qiniu cloud, Use qiniu://<bucket>[/name_of_dir] to deploy to a bucket'
    def on_setup_env(self,**extra):
        self.env.add_publisher('qiniu',qiniuPublisher)

