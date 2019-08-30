import os
import datetime
from dateutil.tz import tzutc
import logging

class S3FSClient:

    def _getRelativePath(self, path):
        import boto3
        try:
            from urllib.parse import urlparse
        except ImportError:
            from urlparse import urlparse

        relPath = path
        uri = urlparse(path)
        self.s3BucketName = uri.netloc
        #self.client = boto3.client('s3')
        endpoint_url = os.environ.get('S3_ENDPOINT_URL')

        # from boto3 import Session
        # Session.client.defaults = (None, None, False, None, endpoint_url, None, None, None, None)

        # import functools
        # boto3.client = functools.partial(boto3.client, endpoint_url=endpoint_url)
        # boto3.resource = functools.partial(boto3.resource, endpoint_url=endpoint_url)

        if endpoint_url:
            self.client = boto3.client(
                's3', 
                endpoint_url=endpoint_url, 
                config=boto3.session.Config(signature_version='s3v4')
            )
        else:
            self.client = boto3.client(
                's3', 
                config=boto3.session.Config(signature_version='s3v4')
            )

        relPath = uri.path[1:]

        relPath = relPath.replace("//", "/")
        if relPath.endswith("/"):
            relPath = relPath[:-1]

        return relPath

    def get_smart_open_transport_params(self):
        transport_params = None
        endpoint_url = os.environ.get('S3_ENDPOINT_URL')

        if endpoint_url:
            transport_params = {
                'resource_kwargs': {
                    'endpoint_url': endpoint_url,
                }
            }
                
        return transport_params

    def s3fs_open(self, path, mode):
        from s3fs.core import S3FileSystem

        endpoint_url = os.environ.get('S3_ENDPOINT_URL')
        client_kwargs = {}
        if endpoint_url:
            client_kwargs = {'endpoint_url': endpoint_url}

        s3 = S3FileSystem(anon=False, default_fill_cache=False, client_kwargs=client_kwargs)
        return s3.open(path, mode=mode)

    def listFolder(self, path, wild=False, removeFolderName=False, meta_info=False):
        import fnmatch

        path = self._getRelativePath(path)
        path_filter = None
        if path and wild:
            parts = path.split('/')
            path = '/'.join(parts[:-1])
            path_filter = parts[-1]

        if path:    
            path = path + "/" if not path.endswith("/") else path

        #print("s3BucketName: %s;Path:%s; path_filter:%s"%(self.s3BucketName, path, path_filter))
    
        ContinuationToken = None
        result = []
        while True:
            if ContinuationToken:
                listFiles = self.client.list_objects_v2(
                    Bucket=self.s3BucketName, Prefix=path, Delimiter='/', ContinuationToken=ContinuationToken)
            else:
                listFiles = self.client.list_objects_v2(
                    Bucket=self.s3BucketName, Prefix=path, Delimiter='/')

            ContinuationToken = listFiles.get('NextContinuationToken', None)
            files = None
            folders = None
            if listFiles is not None:
                files = listFiles.get('Contents')
                folders = listFiles.get('CommonPrefixes')

            if files is not None:
                for file in files:
                    if file.get('Key') != path:
                        file_path = file.get('Key')[len(path):]
                        if meta_info:
                            result.append({'path': file_path, 
                                'last_modified': self._get_seconds_from_epoch(file.get('LastModified')), 'size': file.get('Size', 0)})
                        else:    
                            result.append(file_path)

            if folders is not None:
                for folder in folders:
                    if folder.get('Prefix') != path:
                        folder_path = folder.get('Prefix')[len(path):]
                        if meta_info:
                            result.append({'path': folder_path, 
                                'last_modified': self._get_seconds_from_epoch(folder.get('LastModified')), 'size': folder.get('Size', 0)})
                        else:    
                            result.append(folder_path)

            if not ContinuationToken:
                break

        if path_filter:
            if meta_info:
                result = [item for item in result if fnmatch.fnmatch(item['path'], path_filter)]
            else:    
                result = fnmatch.filter(result, path_filter)

        return result

    def createFolder(self, path):
        path = self._getRelativePath(path)
        path = path + "/" if not path.endswith("/") else path
        self.client.put_object(Bucket=self.s3BucketName, Key=path)

    def createParentFolder(self, path):
        parent = os.path.dirname(path)
        self.createFolder(parent)

    def removeFolder(self, path, remove_self=True):
        path = self._getRelativePath(path)
        self._s3_removeFolder(path, remove_self)

    def removeFile(self, path, wild=False):
        if wild:
            files = self.listFolder(path, wild)
            path = self._getRelativePath(path)
            for file in files:
                path_to_remove = os.path.join(os.path.dirname(path),file)
                #print(path_to_remove)
                self.client.delete_object(Bucket=self.s3BucketName, Key=path_to_remove)

            #raise Exception("S3FSClient::removeFile wild is not implemented:%s"%path)
        else:    
            path = self._getRelativePath(path)
            self.client.delete_object(Bucket=self.s3BucketName, Key=path)

    def _s3_removeFolder(self, path, remove_self=True):
        path = path + "/" if not path.endswith("/") else path

        # print("Remove:%s"%path)
        ContinuationToken = None
        while True:
            if ContinuationToken:
                listFiles = self.client.list_objects_v2(
                    Bucket=self.s3BucketName, Prefix=path, Delimiter='/', ContinuationToken=ContinuationToken)
            else:
                listFiles = self.client.list_objects_v2(
                    Bucket=self.s3BucketName, Prefix=path, Delimiter='/')

            # print(listFiles)
            ContinuationToken = listFiles.get('NextContinuationToken', None)
            files = None
            folders = None
            if listFiles is not None:
                files = listFiles.get('Contents')
                folders = listFiles.get('CommonPrefixes')

            if files is not None:
                for file in files:
                    #print("Delete path:%s"%file.get('Key'))
                    self.client.delete_object(
                        Bucket=self.s3BucketName, Key=file.get('Key'))

            if folders is not None:
                for folder in folders:
                    self._s3_removeFolder(folder.get(
                        'Prefix'), remove_self=False)

            if not ContinuationToken:
                break

        if remove_self:
            self.client.delete_object(Bucket=self.s3BucketName, Key=path)

    def _s3_moveFile(self, oldName, newName):
        self.client.copy_object(Bucket=self.s3BucketName, CopySource={
                                'Bucket': self.s3BucketName, 'Key': oldName}, Key=newName)
        self.client.delete_object(Bucket=self.s3BucketName, Key=oldName)

    # def saveSingleSCV(self, path, new_path):
    #     path = self._getRelativePath(path)
    #     new_path = self._getRelativePath(new_path)

    #     print(path)
    #     print(self.s3BucketName)
    #     listFiles = self.client.list_objects(
    #         Bucket=self.s3BucketName, Prefix=path + "/", Delimiter='/').get('Contents')
    #     for item in listFiles:
    #         file = item.get('Key')
    #         if (file.endswith(".csv")):
    #             self._s3_moveFile(file, new_path)
    #             break

    #     self._s3_removeFolder(path)

    def isFileExists(self, path):
        path = self._getRelativePath(path)
        exists = False
        try:
            res = self.client.head_object(Bucket=self.s3BucketName, Key=path)
            exists = True
        except Exception as e:
            pass

        return exists

    @staticmethod    
    def _get_seconds_from_epoch(date_data):
        res = 0
        try:
            if date_data:
                epoch = datetime.datetime(1970,1,1,tzinfo=tzutc())
                res = (date_data - epoch).total_seconds()
        except Exception as e:
            #logging.exception("_get_seconds_from_epoch failed.")
            pass

        return res
            
    def getMTime(self, path):
        path = self._getRelativePath(path)
        res = None
        try:
            obj = self.client.head_object(Bucket=self.s3BucketName, Key=path)
            res = self._get_seconds_from_epoch(obj.get('LastModified'))
        except Exception as e:
            #logging.exception("getMTime failed.")
            pass

        return res
            
    def getFileSize(self, path):
        path = self._getRelativePath(path)
        res = 0
        try:
            obj = self.client.head_object(Bucket=self.s3BucketName, Key=path)
            res = obj.get('ContentLength')
        except Exception as e:
            #logging.exception("getFileSize failed.")
            pass

        return res
            
    def isDirExists(self, path):
        path = self._getRelativePath(path)
        listFiles = self.client.list_objects(
            Bucket=self.s3BucketName, Prefix=path + "/", Delimiter='/')
        if listFiles is not None:
            content = listFiles.get('Contents')
            if content is None:
                listFiles = listFiles.get('CommonPrefixes')
            else:
                listFiles = content

        #print(listFiles)        
        return listFiles is not None

    def readTextFile(self, path):
        path = self._getRelativePath(path)
        obj = self.client.get_object(Bucket=self.s3BucketName, Key=path)
        return obj['Body'].read()

    def writeTextFile(self, path, data, atomic=False):
        path = self._getRelativePath(path)
        self.client.put_object(Body=data, Bucket=self.s3BucketName, Key=path)

    def copyFileRemote(self, path_src, path_dst):
        path = self._getRelativePath(path_src)
        copy_source = {
            'Bucket': self.s3BucketName,
            'Key': path
        }
        
        path = self._getRelativePath(path_dst)
        self.client.copy(copy_source, self.s3BucketName, path)

    def copyFile(self, path_src, path_dst):
        import boto3

        if path_src.startswith("s3") and path_dst.startswith("s3"):
            self.copyFileRemote(path_src, path_dst)
        elif path_dst.startswith("s3"):    
            path = self._getRelativePath(path_dst)
            s3_config = boto3.s3.transfer.TransferConfig(use_threads=False)
            self.client.upload_file(path_src, Bucket=self.s3BucketName, Key=path, Config=s3_config) 
        elif path_src.startswith("s3"):
            self.downloadFile(path_src, path_dst)

    def copyFiles(self, path_src, path_dst):
        files = self.listFolder(path_src, wild=True)
        for file in files:
            self.copyFile(os.path.join(os.path.dirname(path_src), file), os.path.join(path_dst, file))

    def copyFolder(self, path_src, path_dst):
        from .FSClient import FSClient

        files = FSClient().listFolder(path_src)
        for file in files:
            full_src = os.path.join(path_src, file)
            if FSClient().isFileExists(full_src):
                self.copyFile(full_src, os.path.join(path_dst, file))
            else:
                self.copyFolder(full_src, os.path.join(path_dst, file))

    def downloadFile(self, path, local_path):
        from .LocalFSClient import LocalFSClient
        from .FSClient import FSClient
        import boto3

        if path.startswith("http:") or path.startswith("https:"):
            s3_path = self._getRelativePath(local_path)

            with LocalFSClient().save_atomic(path) as temp_file:
                LocalFSClient().downloadFile(path, temp_file)
                s3_config = boto3.s3.transfer.TransferConfig(use_threads=False)
                self.client.upload_file(temp_file, Bucket=self.s3BucketName, Key=s3_path,
                    Config = s3_config)

                #FSClient().waitForFile(local_path, wait_for_file=True, num_tries=3000, interval_sec=20)
            # with FSClient().open(path, "rb", encoding=None) as fd:
            #     self.client.upload_fileobj(fd, Bucket=self.s3BucketName, Key=s3_path)
        else:    
            path = self._getRelativePath(path)
            LocalFSClient().createParentFolder(local_path)
            self.client.download_file(Bucket=self.s3BucketName, Key=path, Filename=local_path)

    def downloadFolder(self, path, local_path):
        files = self.listFolder(path)
        for file in files:
            if file.endswith('/'):
                self.downloadFolder(os.path.join(path, file), os.path.join(local_path, file))
            else:
                self.copyFile(os.path.join(path, file), os.path.join(local_path, file))   

    def moveFile(self, path_src, path_dst):
        self.copyFile(path_src, path_dst)

        if path_src.startswith("s3"):
            self.removeFile(path_src)
        else:
            from .LocalFSClient import LocalFSClient
            LocalFSClient().removeFile(path_src)    

