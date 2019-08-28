# -*- coding: utf-8 -*-
from tests.base import BaseTest
import os
import tempfile

import fudge
import six
from azure.common import AzureMissingResourceHttpError, AzureHttpError
from botocore.stub import ANY
from fudge.inspector import arg
from google.auth import app_engine, compute_engine
from missinglink.core.exceptions import NotFound, NonRetryException, AccessDenied
from requests import ConnectionError
from six import StringIO, BytesIO
from urllib3.exceptions import ProtocolError

from missinglink.legit.gcp_services import GCPServices, GoogleCredentialsFile, GcpComputeCredentials
from missinglink.legit.gcs_utils import GCSDownloadDirectDownload, do_delete_all, Uploader, Downloader, s3_moniker, \
    _s3_upload_or_transfer, _az_upload_or_transfer, azure_moniker, _az_download, AzureContainerNotFound, \
    _clear_cached_objects, _get_boto_local_client, _get_azure_retry, _WriteWrapperStream, \
    _ReadWrapperStream

import httpretty


try:
    # in py2 you need to call contextmanager function without the () in py3 you need with the ()
    # This will make sure that contextmanager behave the same
    from contextlib2 import contextmanager
except ImportError:
    # noinspection PyUnresolvedReferences
    from contextlib import contextmanager


@contextmanager
def set_s3_env_auth():
    ACCESS_KEY = 'AWS_ACCESS_KEY_ID'
    SECRET_KEY = 'AWS_SECRET_ACCESS_KEY'

    os.environ[ACCESS_KEY] = BaseTest.some_random_shit(ACCESS_KEY)
    os.environ[SECRET_KEY] = BaseTest.some_random_shit(SECRET_KEY)

    yield


class TestGCSOperations(BaseTest):
    bucket_name = 'missinglink-public'
    s3_bucket_name = 's3://missinglink-public'
    gs_bucket_name = 'gs://missinglink-public'
    object_name_1 = 'test_files_dont_delete/1.txt'
    s3_object_name_1 = '{bucket}/{object_name}'.format(bucket=s3_bucket_name, object_name=object_name_1)

    azure_bucket_name = 'az://missinglink-public'
    az_object_name_1 = '{bucket}/{object_name}'.format(bucket=azure_bucket_name, object_name=object_name_1)
    gs_object_name_1 = '{bucket}/{object_name}'.format(bucket=gs_bucket_name, object_name=object_name_1)

    def setUp(self):
        super(TestGCSOperations, self).setUp()

        _clear_cached_objects()

        GoogleCredentialsFile._clear_files_cache()
        GcpComputeCredentials._clear_cached_project_id()

    def _wrap_gcs_local_auth_files(self, actual_test):
        @fudge.patch('missinglink.legit.gcp_services.GoogleCredentialsFile._get_auth_config_from_default_file')
        @fudge.patch('missinglink.legit.gcp_services.GCPServices.get_default_project_id')
        def wrap(mock__get_auth_config_from_default_file, mock_get_default_project_id):
            client_secret = self.some_random_shit('client_secret')
            refresh_token = self.some_random_shit('refresh_token')
            client_id = self.some_random_shit('client_id')

            auth_info = {
                'client_secret': client_secret,
                'refresh_token': refresh_token,
                'client_id': client_id,
                'type': 'authorized_user'
            }

            mock__get_auth_config_from_default_file.expects_call().returns(auth_info)

            project_id = self.some_random_shit('project_id')

            mock_get_default_project_id.expects_call().returns(project_id)

            actual_test()

        wrap()

    def _wrap_azure_local_auth_files(self, actual_test):
        @fudge.patch('missinglink.legit.azure_config.AzureConfig._get_auth_config_from_default_file')
        def wrap(mock__get_auth_config_from_default_file, mock_get_default_project_id):
            client_secret = self.some_random_shit('client_secret')
            refresh_token = self.some_random_shit('refresh_token')
            client_id = self.some_random_shit('client_id')

            auth_info = {
                'client_secret': client_secret,
                'refresh_token': refresh_token,
                'client_id': client_id,
                'type': 'authorized_user'
            }

            mock__get_auth_config_from_default_file.expects_call().returns(auth_info)

            project_id = self.some_random_shit('project_id')

            mock_get_default_project_id.expects_call().returns(project_id)

            actual_test()

        wrap()

    @httpretty.activate
    @fudge.patch('google.cloud.storage.Blob.upload_from_file')
    def test_upload_bucket_gcs(self, mock_upload_from_file):
        def actual_test():
            full_path_to_data = StringIO('1234')
            content_type = self.some_random_shit('content_type')

            mock_upload_from_file.expects_call().with_args(arg.isinstance(_ReadWrapperStream), content_type)

            bucket_name = self.some_random_shit('bucket_name')
            object_name = self.some_random_shit('object_name')

            headers = {'Content-Type': content_type}
            Uploader.upload_bucket(bucket_name, object_name, full_path_to_data, headers)

        self._wrap_gcs_local_auth_files(actual_test)

    @fudge.patch('missinglink.legit.gcp_services.GoogleCredentialsFile.get_credentials')
    def test_upload_bucket_gcs__no_credentials(self, mock__get_file_credentials):
        mock__get_file_credentials.expects_call().returns(lambda: None)

        full_path_to_data = StringIO('1234')
        content_type = self.some_random_shit('content_type')

        bucket_name = self.some_random_shit('bucket_name')
        object_name = self.some_random_shit('object_name')

        headers = {'Content-Type': content_type}

        with self.assertRaises(NonRetryException):
            Uploader.upload_bucket(bucket_name, object_name, full_path_to_data, headers)

    @classmethod
    def _create_temp_empty_file(cls):
        filename = tempfile.mktemp()

        with open(filename, 'wb'):
            pass

        return filename

    @httpretty.activate
    @fudge.patch('missinglink.legit.path_utils.open_file_handle_too_many')
    def test_upload_bucket_gcs_using_filename_raises_io_error(self, mock_open_file_handle_too_many):
        def actual_test():
            full_path_to_data = self._create_temp_empty_file()

            mock_open_file_handle_too_many.expects_call().with_args(full_path_to_data, 'rb').raises(OSError)

            content_type = self.some_random_shit('content_type')

            bucket_name = self.some_random_shit('bucket_name')
            object_name = self.some_random_shit('object_name')

            headers = {'Content-Type': content_type}
            with self.assertRaises(NonRetryException):
                Uploader.upload_bucket(bucket_name, object_name, full_path_to_data, headers)

        self._wrap_gcs_local_auth_files(actual_test)

    @httpretty.activate
    @fudge.patch('google.cloud.storage.Blob.upload_from_file')
    def test_upload_bucket_gcs_using_filename(self, mock_upload_from_file):
        def actual_test():
            full_path_to_data = self._create_temp_empty_file()

            content_type = self.some_random_shit('content_type')

            def is_file(obj):
                return hasattr(obj, 'read')

            mock_upload_from_file.expects_call().with_args(arg.passes_test(is_file), content_type)

            bucket_name = self.some_random_shit('bucket_name')
            object_name = self.some_random_shit('object_name')

            headers = {'Content-Type': content_type}
            Uploader.upload_bucket(bucket_name, object_name, full_path_to_data, headers)

        self._wrap_gcs_local_auth_files(actual_test)

    @httpretty.activate
    @fudge.patch('google.cloud.storage.Blob.upload_from_file')
    def test_upload_bucket_gcs_with_progress(self, mock_upload_from_file):
        def actual_test():
            content = b'1234'
            full_path_to_data = six.BytesIO(content)
            content_type = self.some_random_shit('content_type')

            size = self.some_random_shit_number_int16()

            def fake_mock_upload_from_file(stream, context_type):
                stream.read(size)
                self.assertEqual(len(content), stream.tell())

            mock_upload_from_file.expects_call().with_args(arg.isinstance(_ReadWrapperStream), content_type).calls(fake_mock_upload_from_file)

            bucket_name = self.some_random_shit('bucket_name')
            object_name = self.some_random_shit('object_name')

            fake_progress_callback = fudge.Fake().expects_call().with_args(len(content), None)

            headers = {'Content-Type': content_type}
            Uploader.upload_bucket(bucket_name, object_name, full_path_to_data, headers, progress_callback=fake_progress_callback)

        self._wrap_gcs_local_auth_files(actual_test)

    @httpretty.activate
    @set_s3_env_auth()
    def test_upload_bucket_s3(self):
        import boto3
        from botocore.stub import Stubber

        full_path_to_data = StringIO('1234')
        content_type = self.some_random_shit('content_type')

        bucket_name = self.some_random_shit('bucket_name')
        object_name = self.some_random_shit('object_name')

        s3_client = boto3.client('s3')
        stubber = Stubber(s3_client)
        expected_params = {
            'Bucket': bucket_name,
            'Key': object_name,
            'Body': ANY,
        }
        stubber.add_response('put_object', {}, expected_params)

        headers = {'Content-Type': content_type}
        with stubber:
            _s3_upload_or_transfer(s3_moniker + bucket_name, object_name, full_path_to_data, headers, s3_client=s3_client)

    @httpretty.activate
    @set_s3_env_auth()
    def test_copy_bucket_s3(self):
        import boto3
        from botocore.stub import Stubber

        full_path_to_data = self.some_random_shit('full_path_to_data')
        content_type = self.some_random_shit('content_type')

        bucket_name = self.some_random_shit('bucket_name')
        object_name = self.some_random_shit('object_name')

        s3_client = boto3.client('s3')
        stubber = Stubber(s3_client)
        expected_params = {
            'Bucket': bucket_name,
            'Key': object_name,
            'CopySource': full_path_to_data,
        }
        stubber.add_response('copy_object', {}, expected_params)

        headers = {'Content-Type': content_type}
        with stubber:
            _s3_upload_or_transfer(s3_moniker + bucket_name, object_name, s3_moniker + full_path_to_data, headers, s3_client=s3_client)

    @httpretty.activate
    @fudge.patch('azure.storage.blob.BlockBlobService.create_blob_from_stream')
    def test_upload_bucket_azure(self, mock_create_blob_from_stream):
        full_path_to_data = BytesIO(b'1234')
        content_type = self.some_random_shit('content_type')

        bucket_name = self.some_random_shit('bucket_name')
        object_name = self.some_random_shit('object_name')

        headers = {'Content-Type': content_type}

        mock_create_blob_from_stream.expects_call().with_args(
            bucket_name, object_name, full_path_to_data, metadata={}, content_settings=arg.any(), progress_callback=None)

        storage_account = self.some_random_shit('storage_account')
        storage_key = self.some_random_shit('storage_key')
        fake_azure_config = fudge.Fake().has_attr(storage_account=storage_account, storage_key=storage_key)
        _az_upload_or_transfer(azure_moniker + bucket_name, object_name, full_path_to_data, headers, fake_azure_config)

    @httpretty.activate
    @fudge.patch('azure.storage.blob.BlockBlobService.create_blob_from_stream')
    def test_upload_bucket_azure_full_name(self, mock_create_blob_from_stream):
        full_path_to_data = BytesIO(b'1234')
        content_type = self.some_random_shit('content_type')

        bucket_name = self.some_random_shit('bucket_name')
        object_name = self.some_random_shit('object_name')

        headers = {'Content-Type': content_type}

        mock_create_blob_from_stream.expects_call().with_args(
            bucket_name, object_name, full_path_to_data, metadata={}, content_settings=arg.any(), progress_callback=None)

        storage_account = self.some_random_shit('storage_account')
        storage_key = self.some_random_shit('storage_key')
        fake_azure_config = fudge.Fake().has_attr(storage_key=storage_key)

        full_bucket_name = '%s.%s' % (storage_account, bucket_name)

        _az_upload_or_transfer(azure_moniker + full_bucket_name, object_name, full_path_to_data, headers, fake_azure_config)

    @httpretty.activate
    @fudge.patch('requests.head')
    @fudge.patch('requests.put')
    def test_upload_secure_url_method(self, mock_session_head, mock_session_put):
        full_path_to_data = StringIO('1234')
        content_type = self.some_random_shit('content_type')

        headers = {'Content-Type': content_type}
        head_url = self.some_random_shit('head_url')
        put_url = self.some_random_shit('put_url')

        fake_response = fudge.Fake().has_attr(status_code=404)
        mock_session_head.expects_call().with_args(head_url).returns(fake_response)

        def fake_put(url, data, headers):
            data.read(4)

            fake_put_response = fudge.Fake().has_attr(status_code=200).provides('raise_for_status')

            return fake_put_response

        mock_session_put.expects_call().with_args(put_url, data=arg.any(), headers=headers).calls(fake_put)

        Uploader.upload_http(put_url, head_url, full_path_to_data, headers)

    @httpretty.activate
    @fudge.patch('requests.head')
    @fudge.patch('requests.put')
    def test_upload_secure_url_method_with_progress(self, mock_session_head, mock_session_put):
        content = '1234'
        full_path_to_data = StringIO(content)
        content_type = self.some_random_shit('content_type')

        headers = {'Content-Type': content_type}
        head_url = self.some_random_shit('head_url')
        put_url = self.some_random_shit('put_url')

        fake_response = fudge.Fake().has_attr(status_code=404)
        mock_session_head.expects_call().with_args(head_url).returns(fake_response)

        def fake_put(url, data, headers):
            data.read(4)

            fake_put_response = fudge.Fake().has_attr(status_code=200).provides('raise_for_status')

            return fake_put_response

        mock_session_put.expects_call().with_args(put_url, data=arg.any(), headers=headers).calls(fake_put)

        fake_progress_callback = fudge.Fake().expects_call().with_args(len(content), None)

        Uploader.upload_http(put_url, head_url, full_path_to_data, headers, progress_callback=fake_progress_callback)

    @httpretty.activate
    @fudge.patch('google.cloud.storage.Blob.download_to_file')
    def test_download_no_auth_method_with_bucket(self, mock_download_to_file):
        def actual_test():
            download_result = self.some_random_shit('result').encode('utf-8')

            def write_data(stream):
                stream.write(download_result)

            mock_download_to_file.expects_call().with_args(arg.isinstance(_WriteWrapperStream)).calls(write_data)
            result = Downloader.download_bucket(self.bucket_name, self.object_name_1)
            self.assertEqual(result, download_result)

        self._wrap_gcs_local_auth_files(actual_test)

    @httpretty.activate
    @fudge.patch('missinglink.legit.gcp_services.GoogleCredentialsFile.get_credentials')
    def test_download_gcp__no_credentials(self, mock_get_credentials_from_file):
        mock_get_credentials_from_file.expects_call().returns(lambda: None)

        with self.assertRaises(NonRetryException):
            Downloader.download_bucket(self.gs_bucket_name, self.object_name_1)

    @httpretty.activate
    @fudge.patch('google.cloud.storage.Blob.download_to_file')
    def test_download_no_auth_method_with_bucket_with_progress(self, mock_download_to_file):
        def actual_test():
            download_result = self.some_random_shit('result').encode('utf-8')

            def write_data(stream):
                stream.write(download_result)

            mock_download_to_file.expects_call().with_args(arg.isinstance(_WriteWrapperStream)).calls(write_data)

            mock_progress_callback = fudge.Fake().is_callable().with_args(len(download_result), None)
            result = Downloader.download_bucket(self.bucket_name, self.object_name_1, progress_callback=mock_progress_callback)
            self.assertEqual(result, download_result)

        self._wrap_gcs_local_auth_files(actual_test)

    @httpretty.activate
    @fudge.patch('google.cloud.storage.Blob.download_to_file')
    def test_gcs_download_with_bucket_into_target(self, mock_download_to_file):
        def actual_test():
            fake_target_fileobj = fudge.Fake()
            mock_download_to_file.expects_call().with_args(arg.isinstance(_WriteWrapperStream))

            result = Downloader.download_bucket(None, self.gs_object_name_1, target_fileobj=fake_target_fileobj)
            self.assertIsNone(result)

        self._wrap_gcs_local_auth_files(actual_test)

    @httpretty.activate
    @set_s3_env_auth()
    def test_s3_download_with_bucket_into_target(self):
        s3_client = _get_boto_local_client('s3')

        fake_target_fileobj = fudge.Fake()

        mock_download_fileobj = fudge.Fake().is_callable().with_args(self.bucket_name, self.object_name_1, fake_target_fileobj, Callback=arg.passes_test(callable))

        with fudge.patched_context(s3_client, 'download_fileobj', mock_download_fileobj):
            result = Downloader.download_bucket(None, self.s3_object_name_1, target_fileobj=fake_target_fileobj)
            self.assertIsNone(result)

    @httpretty.activate
    @set_s3_env_auth()
    def test_s3_download(self):
        s3_client = _get_boto_local_client('s3')

        download_result = self.some_random_shit('result').encode('utf-8')

        def fake_download_fileobj(_bucket_name, _object_name, stream, Callback=None):
            stream.write(download_result)

        mock_download_fileobj = fudge.Fake().expects_call().with_args(self.bucket_name, self.object_name_1, arg.isinstance(six.BytesIO), Callback=arg.passes_test(callable)).calls(fake_download_fileobj)

        with fudge.patched_context(s3_client, 'download_fileobj', mock_download_fileobj):
            result = Downloader.download_bucket(self.s3_bucket_name, self.object_name_1)
            self.assertEqual(result, download_result)

    @httpretty.activate
    @set_s3_env_auth()
    def test_s3_download_moniker_in_object_name(self):
        s3_client = _get_boto_local_client('s3')

        download_result = self.some_random_shit('result').encode('utf-8')

        def fake_download_fileobj(_bucket_name, _object_name, stream, Callback=None):
            for _ in range(len(download_result)):
                Callback(1)

            stream.write(download_result)

        mock_progress_callback = fudge.Fake().expects_call()

        for i in range(len(download_result)):
            mock_progress_callback = mock_progress_callback.with_args(i + 1, None)
            is_last = i == len(download_result) - 1
            if not is_last:
                mock_progress_callback = mock_progress_callback.next_call()

        mock_download_fileobj = fudge.Fake().expects_call().with_args(self.bucket_name, self.object_name_1, arg.isinstance(six.BytesIO), Callback=arg.passes_test(callable)).calls(fake_download_fileobj)

        with fudge.patched_context(s3_client, 'download_fileobj', mock_download_fileobj):
            result = Downloader.download_bucket(None, self.s3_object_name_1, progress_callback=mock_progress_callback)
            self.assertEqual(result, download_result)

    @httpretty.activate
    @fudge.patch('azure.storage.blob.BlockBlobService.get_blob_to_bytes')
    def test_azure_download_moniker_in_object_name(self, mock_get_blob_to_bytes):
        content = self.some_random_shit('content')
        fake_azure_response = fudge.Fake().has_attr(content=content)
        mock_get_blob_to_bytes.expects_call().with_args(self.bucket_name, self.object_name_1, progress_callback=None).returns(fake_azure_response)
        storage_account = self.some_random_shit('storage_account')
        storage_key = self.some_random_shit('storage_key')
        fake_azure_config = fudge.Fake().has_attr(storage_account=storage_account, storage_key=storage_key)
        self.assertEqual(Downloader.download_bucket(None, self.az_object_name_1, azure_config=fake_azure_config), content)

    def test__get_azure_retry(self):
        retry = _get_azure_retry()
        fake_context1 = fudge.Fake().has_attr(exception=ConnectionError())
        with self.assertRaises(AzureMissingResourceHttpError):
            retry(fake_context1)

        fake_response1 = fudge.Fake().has_attr(status=None)
        fake_request1 = fudge.Fake().has_attr(body=None)

        fake_context2 = fudge.Fake().has_attr(exception=ConnectionError(ProtocolError()), response=fake_response1, request=fake_request1)
        self.assertTrue(retry(fake_context2))

        fake_context2 = fudge.Fake().has_attr(exception=AzureHttpError(None, 403))
        with self.assertRaises(AccessDenied):
            retry(fake_context2)

    @httpretty.activate
    @fudge.patch('azure.storage.blob.BlockBlobService.get_blob_to_bytes')
    def test_azure_download(self, mock_get_blob_to_bytes):
        storage_account = self.some_random_shit('storage_account')
        storage_key = self.some_random_shit('storage_key')
        fake_azure_config = fudge.Fake().has_attr(storage_account=storage_account, storage_key=storage_key)

        bucket_name = self.some_random_shit('bucket_name')
        object_name = self.some_random_shit('object_name')

        content_data = self.some_random_shit('content')
        content_blob = fudge.Fake().has_attr(content=content_data)

        mock_get_blob_to_bytes.expects_call().with_args(bucket_name, object_name, progress_callback=None).returns(content_blob)

        self.assertEqual(_az_download(bucket_name, object_name, azure_config=fake_azure_config), content_data)

    @httpretty.activate
    @fudge.patch('azure.storage.blob.BlockBlobService.get_blob_to_stream')
    def test_azure_download_to_target(self, mock_get_blob_to_stream):
        storage_account = self.some_random_shit('storage_account')
        storage_key = self.some_random_shit('storage_key')
        fake_azure_config = fudge.Fake().has_attr(storage_account=storage_account, storage_key=storage_key)

        bucket_name = self.some_random_shit('bucket_name')
        object_name = self.some_random_shit('object_name')

        fake_target_fileobj = fudge.Fake().has_attr(seekable=True)

        mock_get_blob_to_stream.expects_call().with_args(bucket_name, object_name, fake_target_fileobj, progress_callback=None)

        self.assertIsNone(_az_download(bucket_name, object_name, azure_config=fake_azure_config, target_fileobj=fake_target_fileobj))

    @httpretty.activate
    @fudge.patch('azure.storage.blob.BlockBlobService.get_blob_to_bytes')
    @fudge.patch('time.sleep')
    def test_azure_download_raises_AzureMissingResourceHttpError(self, mock_get_blob_to_bytes, mock_sleep):
        from azure.common import AzureMissingResourceHttpError

        storage_account = self.some_random_shit('storage_account')
        storage_key = self.some_random_shit('storage_key')
        fake_azure_config = fudge.Fake().has_attr(storage_account=storage_account, storage_key=storage_key)

        bucket_name = self.some_random_shit('bucket_name')
        object_name = self.some_random_shit('object_name')

        message = self.some_random_shit('message')
        status_code = self.some_random_shit_number_int63()

        mock_get_blob_to_bytes.expects_call().with_args(bucket_name, object_name, progress_callback=None).raises(AzureMissingResourceHttpError(message, status_code))
        mock_sleep.expects_call().times_called(9)

        with self.assertRaises(AzureContainerNotFound):
            _az_download(bucket_name, object_name, azure_config=fake_azure_config)

    @httpretty.activate
    @fudge.patch('azure.storage.blob.BlockBlobService.get_blob_to_bytes')
    def test_azure_download_with_full_bucket_name(self, mock_get_blob_to_bytes):
        storage_account = self.some_random_shit('storage_account')
        storage_key = self.some_random_shit('storage_key')
        fake_azure_config = fudge.Fake().has_attr(storage_key=storage_key)

        bucket_name = self.some_random_shit('bucket_name')

        full_bucket_name = '%s.%s' % (storage_account, bucket_name)
        object_name = self.some_random_shit('object_name')

        content_data = self.some_random_shit('content')
        content_blob = fudge.Fake().has_attr(content=content_data)

        mock_get_blob_to_bytes.expects_call().with_args(bucket_name, object_name, progress_callback=None).returns(content_blob)

        self.assertEqual(_az_download(full_bucket_name, object_name, azure_config=fake_azure_config), content_data)

    @httpretty.activate
    @fudge.patch('msrestazure.azure_active_directory.MSIAuthentication.__init__')
    @fudge.patch('missinglink.legit.azure_config.create_storage_client')
    @fudge.patch('azure.storage.blob.BlockBlobService.get_blob_to_bytes')
    def test_azure_download_with_full_bucket_name_under_msi(self, mock__msi_init, mock_create_storage_client, mock_get_blob_to_bytes):
        from msrestazure.azure_active_directory import MSIAuthentication

        storage_account1 = self.some_random_shit('storage_account1')
        storage_account2 = self.some_random_shit('storage_account2')

        access_key = self.some_random_shit('access_key')
        fake_azure_config = fudge.Fake().has_attr(storage_key=None).provides('set_storage_key_env_var').with_args(access_key).times_called(1)

        bucket_name = self.some_random_shit('bucket_name')

        full_bucket_name = '%s.%s' % (storage_account2, bucket_name)
        object_name = self.some_random_shit('object_name')

        content_data = self.some_random_shit('content')
        content_blob = fudge.Fake().has_attr(content=content_data)

        mock_get_blob_to_bytes.expects_call().with_args(bucket_name, object_name, progress_callback=None).returns(content_blob)

        subscription_id = self.some_random_shit('subscription_id')
        ml_instance_role = self.some_random_shit('/subscriptions/%s/' % subscription_id)

        mock__msi_init.expects_call().with_args(msi_res_id=ml_instance_role)

        resource_group1 = self.some_random_shit('resource_group1')
        resource_group_id1 = self.some_random_shit('resourceGroups/%s/' % resource_group1)
        fake_item1 = fudge.Fake().has_attr(id=resource_group_id1, name=storage_account1)

        resource_group2 = self.some_random_shit('resource_group1')
        resource_group_id2 = self.some_random_shit('resourceGroups/%s/' % resource_group2)
        fake_item2 = fudge.Fake().has_attr(id=resource_group_id2, name=storage_account2)
        fake_keys = fudge.Fake().has_attr(keys=[fudge.Fake().has_attr(value=access_key)])

        fake_storage_accounts = fudge.Fake().provides('list').returns([fake_item1, fake_item2]).provides('list_keys').with_args(resource_group2, storage_account2).returns(fake_keys)

        fake_storage_client = fudge.Fake().has_attr(storage_accounts=fake_storage_accounts)
        mock_create_storage_client.expects_call().with_args(arg.isinstance(MSIAuthentication), subscription_id).returns(fake_storage_client)

        os.environ['ML_INSTANCE_ROLE'] = ml_instance_role
        try:
            self.assertEqual(_az_download(full_bucket_name, object_name, azure_config=fake_azure_config), content_data)
        finally:
            del os.environ['ML_INSTANCE_ROLE']

    @httpretty.activate
    @fudge.patch('requests.get')
    def test_download_using_secure_url(self, mock_requests_get):
        singed_url = self.some_random_shit('singed_url')
        content = self.some_random_shit('content').encode('utf-8')
        fake_response = fudge.Fake().provides('raise_for_status').has_attr(content=content, headers={}).expects('iter_content').returns((content, ))
        mock_requests_get.expects_call().with_args(singed_url, stream=True).returns(fake_response)

        result = Downloader.download_http(singed_url)
        self.assertEqual(result, content)

    @httpretty.activate
    @fudge.patch('requests.get')
    def test_download_using_secure_url_with_progress(self, mock_requests_get):
        singed_url = self.some_random_shit('singed_url')
        content = self.some_random_shit('content').encode('utf-8')
        fake_response = fudge.Fake().provides('raise_for_status').has_attr(content=content, headers={'content-length': len(content)}).expects('iter_content').returns((content[:4], content[4:]))
        mock_requests_get.expects_call().with_args(singed_url, stream=True).returns(fake_response)

        mock_progress_callback = fudge.Fake().is_callable().with_args(len(content), 4).next_call().with_args(len(content), len(content))

        result = Downloader.download_http(singed_url, progress_callback=mock_progress_callback)
        self.assertEqual(result, content)

    @httpretty.activate
    @fudge.patch('requests.get')
    def test_download_using_secure_url_returns_404(self, mock_requests_get):
        import requests

        singed_url = self.some_random_shit('singed_url')
        fake_response = fudge.Fake().has_attr(status_code=404)
        fake_response = fudge.Fake().expects('raise_for_status').raises(requests.exceptions.HTTPError(response=fake_response))
        mock_requests_get.expects_call().with_args(singed_url, stream=True).returns(fake_response)

        with self.assertRaises(NotFound):
            Downloader.download_http(singed_url)

    @httpretty.activate
    @fudge.patch('requests.get')
    def test_download_using_secure_url_returns_400(self, mock_requests_get):
        import requests

        singed_url = self.some_random_shit('singed_url')
        fake_response = fudge.Fake().has_attr(status_code=400)
        fake_response = fudge.Fake().expects('raise_for_status').raises(requests.exceptions.HTTPError(response=fake_response))
        mock_requests_get.expects_call().with_args(singed_url, stream=True).returns(fake_response)

        with self.assertRaises(NonRetryException):
            Downloader.download_http(singed_url)

    @httpretty.activate
    @fudge.patch('requests.get')
    def test_download_using_secure_url_with_target_fileobj(self, mock_requests_get):
        singed_url = self.some_random_shit('singed_url')
        chunk1 = self.some_random_shit('chunk1')
        chunk2 = self.some_random_shit('chunk1')
        fake_response = fudge.Fake().has_attr(headers={}).expects('raise_for_status').expects('iter_content').returns([chunk1, chunk2])
        mock_requests_get.expects_call().with_args(singed_url, stream=True).returns(fake_response)

        fake_fileobj = fudge.Fake().expects('write').with_args(chunk1).next_call().with_args(chunk2)
        result = Downloader.download_http(singed_url, target_fileobj=fake_fileobj)
        self.assertIsNone(result)

    @httpretty.activate
    @fudge.patch('google.cloud.storage.Blob.download_to_file')
    def test_download_under_gae(self, mock_download_to_file):
        download_result = self.some_random_shit('result')
        download_result = self.some_random_shit('result').encode('utf-8')

        def write_data(stream):
            stream.write(download_result)

        mock_download_to_file.expects_call().with_args(arg.isinstance(_WriteWrapperStream)).calls(write_data)

        access_token = self.some_random_shit('access_token')
        project_id = self.some_random_shit('project_id')
        ttl = 3600
        app_engine.app_identity = fudge.Fake().provides('get_access_token').returns((access_token, ttl)).provides('get_application_id').returns(project_id)
        credentials = GCPServices.gcp_default_credentials(scopes=['read-only'])
        try:
            result = GCSDownloadDirectDownload(credentials).download(self.bucket_name, self.object_name_1)
            self.assertEqual(result, download_result)
        finally:
            app_engine.app_identity = None

    @httpretty.activate
    @fudge.patch('google.cloud.storage.Blob.download_to_file')
    @fudge.patch('google.auth.default')
    @fudge.patch('requests.Session.get')
    @fudge.patch('missinglink.legit.gcp_services.GoogleCredentialsFile.get_credentials')
    @fudge.patch('missinglink.legit.gcp_services.GoogleCredentialsFile.get_project_id')
    def test_download_under_gcp_compute(self, mock_download_to_file, mock_default_google_auth, mock_requests_get,
                                        mock_get_credentials_from_file, mock_get_project_from_file):
        download_result = self.some_random_shit('result').encode('utf-8')

        def write_data(stream):
            stream.write(download_result)

        mock_download_to_file.expects_call().with_args(arg.isinstance(_WriteWrapperStream)).calls(write_data)

        fake_credentials = (compute_engine.credentials.Credentials(), None)

        mock_default_google_auth.expects_call().returns(fake_credentials)

        mock_get_credentials_from_file.expects_call().returns(lambda: None)
        mock_get_project_from_file.expects_call().returns(None)

        fake_response = self.Expando(text=self.some_random_shit(), raise_for_status=fudge.Fake().is_callable())

        mock_requests_get.expects_call().returns(fake_response)

        credentials = GCPServices.gcp_default_credentials(scopes=['read-only'])

        result = GCSDownloadDirectDownload(credentials).download(self.bucket_name, self.object_name_1)

        self.assertEqual(result, download_result)
        self.assertEqual(fake_credentials[0], credentials)

    @httpretty.activate
    @fudge.patch('google.auth.default')
    @fudge.patch('missinglink.legit.gcp_services.GoogleCredentialsFile.get_credentials')
    def test_download_gcp_compute_default_auth_exception(self, mock_default_google_auth,
                                                         mock_get_credentials_from_file):
        from google.auth import exceptions

        mock_default_google_auth.expects_call().raises(exceptions.DefaultCredentialsError)

        mock_get_credentials_from_file.expects_call().returns(lambda: None)

        with self.assertRaises(exceptions.DefaultCredentialsError):
            GCPServices.gcp_default_credentials(scopes=['read-only'])

    @httpretty.activate
    @fudge.patch('google.auth.default')
    @fudge.patch('missinglink.legit.gcp_services.GoogleCredentialsFile.get_credentials')
    def test_download_gcp_compute_wrong_credentials_type(self, mock_default_google_auth,
                                                         mock_get_credentials_from_file):
        from google.oauth2.credentials import Credentials
        from google.auth import exceptions

        fake_non_compute_credentials = (Credentials(self.some_random_shit()), None)

        mock_default_google_auth.expects_call().returns(fake_non_compute_credentials)

        mock_get_credentials_from_file.expects_call().returns(lambda: None)

        with self.assertRaises(exceptions.DefaultCredentialsError):
            GCPServices.gcp_default_credentials(scopes=['read-only'])

    @httpretty.activate
    @fudge.patch('requests.Session.get')
    def test_get_project_id_from_gcp_compute_instance__no_metadata(self, mock_requests_get):
        from requests.exceptions import ConnectionError

        mock_requests_get.expects_call().raises(ConnectionError)

        project_id = GcpComputeCredentials.get_project_id()

        self.assertIsNone(project_id)

    @httpretty.activate
    @fudge.patch('requests.Session.get')
    def test_get_project_id_from_gcp_compute_instance__from_cache(self, mock_requests_get):
        project_id = self.some_random_shit('project_id')

        fake_response = self.Expando(text=project_id, raise_for_status=fudge.Fake().is_callable())

        mock_requests_get.expects_call().times_called(1).returns(fake_response)

        self.assertEqual(project_id, GcpComputeCredentials.get_project_id())

        # from cache
        self.assertEqual(project_id, GcpComputeCredentials.get_project_id())

    @httpretty.activate
    @fudge.patch('google.cloud.storage.Bucket.list_blobs')
    @fudge.patch('google.cloud.storage.Bucket.delete_blob')
    def test_delete_all(self, mock_list_blobs, mock_delete_blob):
        def actual_test():
            volume_id = self.some_random_shit_number_int63()

            fake_blob1 = fudge.Fake().has_attr(name='1')
            mock_list_blobs.expects_call().with_args(prefix=str(volume_id)).returns([fake_blob1])
            mock_delete_blob.expects_call().with_args('1')

            bucket_name = self.some_random_shit('bucket_name')
            max_files = 1000
            do_delete_all(bucket_name, volume_id, max_files)

        self._wrap_gcs_local_auth_files(actual_test)
