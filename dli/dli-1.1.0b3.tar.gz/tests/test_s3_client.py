import os
import tempfile
import pytest

from unittest import TestCase
from unittest.mock import patch
from boto3 import Session
from botocore.exceptions import ClientError

from dli.client.exceptions import InsufficientPrivilegesException, S3FileDoesNotExist
from dli.client.s3 import Client, S3DatafileWrapper
from tests.localstack_helper import _fake_aws_credentials


session = Session(**_fake_aws_credentials())


@pytest.mark.integration
class S3ClientTestCase(TestCase):

    def setUp(self):
        self.target = Client(session)
        bucket = self.target.s3_resource.Bucket('bucket')
        bucket.create()

        def cleanup():
            bucket.objects.all().delete()
            bucket.delete()

        self.addCleanup(cleanup)

    def test_download_file_validates_destination_is_a_directory(self):
        self.target.s3fs.put(__file__, "s3://bucket/file")
        with self.assertRaises(NotADirectoryError):
            with tempfile.NamedTemporaryFile() as cm:
                self.target.download_files_from_s3_path("s3://bucket/file", cm.name)

    def test_download_file_creates_destination_directory_if_it_does_not_exist(self):
        self.target.s3fs.put(
            __file__,
            os.path.join("s3://bucket/location/", os.path.basename(__file__))
        )

        with tempfile.TemporaryDirectory() as dest:
            dest = os.path.join(dest, "dir1", "dir2")
            self.target.download_files_from_s3_path(
                "s3://bucket/location/test_s3_client.py",
                dest
            )

            self.assertTrue(os.path.exists(dest) and os.path.isdir(dest))
            self.assertTrue(os.path.exists(os.path.join(dest, "location", "test_s3_client.py")))

    def test_download_file_can_download_folders(self):
        self.target.s3fs.put(__file__, "s3://bucket/tdfcdf/file1.txt")
        self.target.s3fs.put(__file__, "s3://bucket/tdfcdf/subdir/file2.txt")
        self.target.s3fs.put(__file__, "s3://bucket/tdfcdf/subdir/subdir/file3.txt")

        with tempfile.TemporaryDirectory() as dest:
            self.target.download_files_from_s3_path("s3://bucket/tdfcdf", dest)

            self.assertTrue(os.path.exists(dest))
            self.assertTrue(os.path.exists(os.path.join(dest, "tdfcdf", "file1.txt")))
            self.assertTrue(os.path.exists(os.path.join(dest, "tdfcdf", "subdir", "file2.txt")))
            self.assertTrue(os.path.exists(os.path.join(dest, "tdfcdf", "subdir", "subdir", "file3.txt")))

    def test_download_file_can_download_single_file(self):
        self.target.s3fs.put(__file__, "s3://bucket/tdfcdf/file1.txt")

        with tempfile.TemporaryDirectory() as dest:
            self.target.download_files_from_s3_path("s3://bucket/tdfcdf/file1.txt", dest)

            self.assertTrue(os.path.exists(dest))
            self.assertTrue(os.path.exists(os.path.join(dest, "tdfcdf", "file1.txt")))


@pytest.mark.integration
class S3DatafileWrapperTestCase(TestCase):

    def setUp(self):
        self.client = Client(session)
        self.s3fs = self.client.s3fs
        bucket = self.client.s3_resource.Bucket('bucket')
        bucket.create()

        def cleanup():
            bucket.objects.all().delete()
            bucket.delete()

        self.addCleanup(cleanup)

    def test_files_returns_files_in_datafile(self):
        files = [
            "s3://bucket/tfrfid/a",
            "s3://bucket/tfrfid/b",
            "s3://bucket/tfrfid/c",
        ]

        for f in files:
            self.s3fs.touch(f)

        datafile = {
            "files": [{"path": f} for f in files]
        }

        target = S3DatafileWrapper(datafile, self.client)
        self.assertCountEqual(
            target.files,
            [f.replace("s3://", "") for f in files]
        )

    def test_files_will_recurse_directories(self):
        files = [
            "s3://bucket/tfwrd/a/aa",
            "s3://bucket/tfwrd/b/bb/bbb",
            "s3://bucket/tfwrd/c/cc/ccc/cccc1",
            "s3://bucket/tfwrd/c/cc/ccc/cccc2",
        ]

        # create sample files
        for f in files:
            self.s3fs.touch(f)

        datafile = {
            "files": [
                {'path': 's3://bucket/tfwrd/a'},
                {'path': 's3://bucket/tfwrd/b'},
                {'path': 's3://bucket/tfwrd/c'}
            ]
        }

        target = S3DatafileWrapper(datafile, self.client)

        self.assertCountEqual(
            target.files,
            [f.replace("s3://", "") for f in files]
        )

    def test_only_files_in_datafile_are_displayed(self):
        files = [
            "s3://bucket/tofidad/a",
            "s3://bucket/tofidad/b",
            "s3://bucket/tofidad/c",
            "s3://bucket/tofidad/d"
        ]

        # create sample files
        for f in files:
            self.s3fs.touch(f)

        datafile = {
            "files": [{"path": f} for f in files[0:1]]
        }
        target = S3DatafileWrapper(datafile, self.client)
        self.assertCountEqual(
            target.files,
            [f.replace("s3://", "") for f in files[0:1]]
        )

    def test_can_open_file(self):
        files = [
            "s3://bucket/tcof/a"
        ]
        # create sample files
        for f in files:
            self.s3fs.touch(f)
            with self.s3fs.open(f, mode="wb") as s3f:
                s3f.write(b"test 1")
                s3f.flush()

        datafile = {
            "files":  [{"path": f} for f in files]
        }

        target = S3DatafileWrapper(datafile, self.client)

        with target.open_file("bucket/tcof/a") as s3file:
            assert s3file is not None
            assert s3file.read() == b"test 1"

    def test_unknown_file_is_handled_gracefully(self):
        files = [
            "s3://bucket/tufihg/a"
        ]
        # create sample files
        for f in files:
            self.s3fs.touch(f)

        datafile = {
            "files": [{"path": f} for f in files]
        }

        target = S3DatafileWrapper(datafile, self.client)

        with self.assertRaises(S3FileDoesNotExist):
            res = target.open_file("bucket/unknown/file")


class S3UploadTestCase(TestCase):

    def setUp(self):
        self.patcher = patch('s3fs.S3FileSystem')
        self.mock_s3fs_instance = self.patcher.start().return_value
        client = Client(session)
        self.s3_client = client

        self.bucket = client.s3_resource.Bucket('s3_test')
        self.bucket.create()

        def cleanup():
            self.bucket.objects.all().delete()
            self.bucket.delete()

        self.addCleanup(cleanup)

        self.s3_location = 's3_test/temp/'

    def test_upload_files_to_s3_normal(self):
        # create some dummy files
        temp_file_list = [tempfile.NamedTemporaryFile() for i in range(3)]
        temp_file_path_list = [f.name for f in temp_file_list]

        expected_s3_location_list = [{
            "path": "s3://{}{}".format(self.s3_location, os.path.basename(file)),
            "size": 0
        } for file in temp_file_path_list]

        upload_result = self.s3_client.upload_files_to_s3(temp_file_path_list, self.s3_location)
        for temp_file in temp_file_list:
            temp_file.close()

        assert len(list(self.bucket.objects.all())) == 3
        self.assertCountEqual(upload_result, expected_s3_location_list)

    def test_upload_files_with_no_bucket_access_fails(self):
        error = ClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access Denied'}},
            'NOOP'
        )

        with patch.object(self.s3_client, 's3_client') as patched_s3_client:
            patched_s3_client.upload_file.side_effect = (
                error
            )

            with self.assertRaises(InsufficientPrivilegesException):
                self.s3_client.upload_files_to_s3([os.path.relpath(__file__)], self.s3_location)

    def tearDown(self):
        self.patcher.stop()
