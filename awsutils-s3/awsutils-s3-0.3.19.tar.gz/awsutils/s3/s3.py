import os
from dirutility import SystemCommand

from awsutils.s3.commands import S3Commands
from awsutils.s3.url import url_validator, bucket_name, bucket_uri, bucket_url

ACL = ('public-read', 'private', 'public-read-write')


def assert_acl(acl):
    """Validate an ACL value by confirming it is in the list of ACL options."""
    assert acl in ACL, "ERROR: Invalid ACL parameter ({0})".format(', '.join("'{0}'".format(i) for i in ACL))
    return True


def remote_path_root(remote_path):
    """Return a remote_path referring to the S3 bucket's root if not specified."""
    if len(remote_path) > 0 and '.' not in os.path.basename(remote_path) and not remote_path.endswith('/'):
        return '{0}/'.format(remote_path)
    else:
        return remote_path


def is_recursive_needed(*uris, recursive_default):
    """
    Checks to see if a recursive flag is needed for a `copy` or `move` command.

    If both URI's are not directories, original recursive value is returned.

    :param uris: S3 URI's
    :param recursive_default: Default value for recursive flag
    :return: Bool, true if both are directories
    """
    return True if all('.' not in os.path.basename(uri) for uri in uris) else recursive_default


class S3:
    def __init__(self, bucket, accelerate=True, quiet=False):
        """
        AWS CLI S3 wrapper.

        https://docs.aws.amazon.com/cli/latest/reference/s3/

        :param bucket: S3 bucket name or S3 bucket url
        :param accelerate: Enable transfer acceleration
        :param quiet: When true, does not display the operations performed from the specified command
        """
        # Extract the bucket name from the url if bucket var is a url
        self.bucket_name = bucket if not url_validator(bucket) else bucket_name(bucket)
        self.accelerate = accelerate
        self.quiet = quiet
        self.cmd = S3Commands()

    @property
    def bucket_uri(self):
        """Retrieve a S3 bucket name in URI form."""
        return bucket_uri(self.bucket_name)

    @property
    def bucket_url(self):
        """Retrieve a url endpoint for a S3 bucket."""
        return bucket_url(self.bucket_name, self.accelerate)

    @property
    def buckets(self):
        """
        List all available S3 buckets.

        Execute the `aws s3 ls` command and decode the output
        """
        return [out.rsplit(' ', 1)[-1] for out in SystemCommand(self.cmd.list())]

    def list(self, remote_path='', recursive=False, human_readable=False, summarize=False):
        """
        List files/folders in a S3 bucket path.

        Optionally, return information on file size on each objects as
        well as summary info.

        :param remote_path: Path to object root in S3 bucket
        :param recursive: Recursively list files/folders
        :param human_readable: Displays file sizes in human readable format
        :param summarize: Displays summary information (number of objects, total size)
        :return:
        """
        return [out.rsplit(' ', 1)[-1] for out in
                SystemCommand(self.cmd.list(uri='{0}/{1}'.format(self.bucket_uri, remote_path_root(remote_path)),
                                            recursive=recursive, human_readable=human_readable, summarize=summarize))]

    def copy(self, src_path, dst_path, dst_bucket=None, recursive=False, include=None, exclude=None, acl='private',
             quiet=None):
        """
        Copy an S3 file or folder to another

        :param src_path: Path to source file or folder in S3 bucket
        :param dst_path: Path to destination file or folder
        :param dst_bucket: Bucket to copy to, defaults to same bucket
        :param recursive: Recursively copy all files within the directory
        :param include: Don't exclude files or objects in the command that match the specified pattern
        :param exclude: Exclude all files or objects from the command that matches the specified pattern
        :param acl: Access permissions, must be either 'private', 'public-read' or 'public-read-write'
        :param quiet: When true, does not display the operations performed from the specified command

        More on inclusion and exclusion parameters...
        http://docs.aws.amazon.com/cli/latest/reference/s3/index.html#use-of-exclude-and-include-filters
        """
        uri1 = '{uri}/{src}'.format(uri=self.bucket_uri, src=src_path)
        uri2 = '{uri}/{dst}'.format(uri=bucket_uri(dst_bucket) if dst_bucket else self.bucket_uri, dst=dst_path)

        # Copy recursively if both URI's are directories and NOT files
        return SystemCommand(
            self.cmd.copy(object1=uri1,
                          object2=uri2,
                          recursive=is_recursive_needed(uri1, uri2, recursive_default=recursive),
                          include=include,
                          exclude=exclude,
                          acl=acl,
                          quiet=quiet if quiet else self.quiet)
        )

    def move(self, src_path, dst_path, dst_bucket=None, recursive=False, include=None, exclude=None):
        """
        Move an S3 file or folder to another

        :param src_path: Path to source file or folder in S3 bucket
        :param dst_path: Path to destination file or folder
        :param dst_bucket: Bucket to copy to, defaults to same bucket
        :param recursive: Recursively copy all files within the directory
        :param include: Don't exclude files or objects in the command that match the specified pattern
        :param exclude: Exclude all files or objects from the command that matches the specified pattern

        More on inclusion and exclusion parameters...
        http://docs.aws.amazon.com/cli/latest/reference/s3/index.html#use-of-exclude-and-include-filters
        """
        uri1 = '{uri}/{src}'.format(uri=self.bucket_uri, src=src_path)
        uri2 = '{uri}/{dst}'.format(uri=bucket_uri(dst_bucket) if dst_bucket else self.bucket_uri, dst=dst_path)

        # Move recursively if both URI's are directories and NOT files
        return SystemCommand(
            self.cmd.move(object1=uri1,
                          object2=uri2,
                          recursive=is_recursive_needed(uri1, uri2, recursive_default=recursive),
                          include=include,
                          exclude=exclude)
        )

    def exists(self, remote_path):
        """
        Check to see if an S3 key (file or directory) exists
        :return: Bool
        """
        # Check to see if a result was returned, if not then key does not exist
        return True if len(SystemCommand(self.cmd.list('{0}/{1}'.format(self.bucket_uri, remote_path)))) > 0 else False

    def delete(self, remote_path, recursive=False, include=None, exclude=None):
        """
        Delete an S3 object from a bucket.

        :param remote_path: Path to S3 object relative to bucket root
        :param recursive: Recursively copy all files within the directory
        :param include: Don't exclude files or objects in the command that match the specified pattern
        :param exclude: Exclude all files or objects from the command that matches the specified pattern
        :return: Command string
        """
        # Delete recursively if both URI's are directories and NOT files
        return SystemCommand(
            self.cmd.remove(uri='{uri}/{src}'.format(uri=self.bucket_uri, src=remote_path),
                            recursive=is_recursive_needed(remote_path, recursive_default=recursive),
                            include=include,
                            exclude=exclude)
        )

    def upload(self, local_path, remote_path=None, acl='private', quiet=None):
        """
        Upload a local file to an S3 bucket.

        :param local_path: Path to file on local disk
        :param remote_path: S3 key, aka remote path relative to S3 bucket's root
        :param acl: Access permissions, must be either 'private', 'public-read' or 'public-read-write'
        :param quiet: When true, does not display the operations performed from the specified command
        """
        # Recursively upload files if the local target is a folder
        # Use local_path file/folder name as remote_path if none is specified
        remote_path = os.path.basename(local_path) if not remote_path else remote_path
        assert_acl(acl)
        return SystemCommand(
            self.cmd.copy(object1=local_path,
                          object2='{0}/{1}'.format(self.bucket_uri, remote_path),
                          recursive=True if os.path.isdir(local_path) else False,
                          acl=acl, quiet=quiet if quiet else self.quiet)
        )

    def download(self, remote_path, local_path=os.getcwd(), recursive=False, quiet=None):
        """
        Download a file or folder from an S3 bucket.

        :param remote_path: S3 key, aka remote path relative to S3 bucket's root
        :param local_path: Path to file on local disk
        :param recursive: Recursively download files/folders
        :param quiet: When true, does not display the operations performed from the specified command
        """
        return SystemCommand(
            self.cmd.copy(object1='{0}/{1}'.format(self.bucket_uri, remote_path),
                          object2=local_path,
                          recursive=recursive,
                          quiet=quiet if quiet else self.quiet)
        )

    def sync(self, local_path, remote_path=None, delete=False, acl='private', quiet=None, remote_source=False):
        """
        Synchronize local files with an S3 bucket.

        S3 sync only copies missing or outdated files or objects between
        the source and target.  However, you can also supply the --delete
        option to remove files or objects from the target that are not
        present in the source.

        :param local_path: Local source directory
        :param remote_path: Destination directory (relative to bucket root)
        :param delete: Sync with deletion, disabled by default
        :param acl: Access permissions, must be either 'private', 'public-read' or 'public-read-write'
        :param quiet: When true, does not display the operations performed from the specified command
        :param remote_source: When true, remote_path is used as the source instead of destination
        """
        assert_acl(acl)
        uri = '{0}/{1}'.format(self.bucket_uri, os.path.basename(local_path) if not remote_path else remote_path)

        # Sync from the S3 bucket
        destination, source = (local_path, uri) if remote_source else (uri, local_path)

        return SystemCommand(
            self.cmd.sync(
                source=source,
                destination=destination,
                delete=delete,
                acl=acl,
                quiet=quiet if quiet else self.quiet)
        )

    def create_bucket(self, region='us-east-1'):
        """
        Create a new S3 bucket.

        :param region: Bucket's hosting region
        """
        # Validate that the bucket does not already exist
        assert self.bucket_name not in self.buckets, 'ERROR: Bucket `{0}` already exists.'.format(self.bucket_name)
        return SystemCommand(self.cmd.make_bucket(self.bucket_uri, region))

    def delete_bucket(self, force=False):
        """
        Deletes an empty S3 bucket. A bucket must be completely empty of objects and versioned
        objects before it can be deleted. However, the force parameter can be used to delete
        the non-versioned objects in the bucket before the bucket is deleted.

        :param force: Deletes all objects in the bucket including the bucket itself
        """
        # Validate that the bucket does exist
        assert self.bucket_name in self.buckets, 'ERROR: Bucket `{0}` does not exists.'.format(self.bucket_name)
        return SystemCommand(self.cmd.remove_bucket(self.bucket_uri, force))

    def pre_sign(self, remote_path, expiration=3600):
        """
        Generate a pre-signed URL for an Amazon S3 object.

        This allows anyone who receives the pre-signed URL to retrieve the S3 object
        with an HTTP GET request.

        :param remote_path: Path to S3 object relative to bucket root
        :param expiration: Number of seconds until the pre-signed URL expires
        :return:
        """
        return SystemCommand(self.cmd.pre_sign('{uri}/{src}'.format(uri=self.bucket_uri, src=remote_path),
                                               expiration))[0]

    def url(self, remote_path):
        """Retrieve a S3 bucket URL for a S3 object."""
        return '{url}/{src}'.format(url=self.bucket_url, src=remote_path)
