def clean_path(path):
    """Return a path string with double quote wrappers if the path contains a space."""
    return '"{0}"'.format(path) if path and '"' not in path else "'{0}'".format(path)


def move_or_copy(command, object1, object2, recursive=False, include=None, exclude=None, acl='private', quiet=True):
    """
    Copy file(s)/folder(s) from one S3 bucket location to another

    :param command: Execute a 'move' or a 'copy' command
    :param object1: S3 uri or file path #1
    :param object2: S3 uri or file path #2
    :param recursive: Recursively copy all files within the directory
    :param include: Don't exclude files or objects in the command that match the specified pattern
    :param exclude: Exclude all files or objects from the command that matches the specified pattern
    :param acl: Access permissions, must be either 'private', 'public-read' or 'public-read-write'
    :param quiet: When true, does not display the operations performed from the specified command
    :return: Command string
    """
    # Determine if we're executing a 'move' or a 'copy' command
    assert command in ('cp', 'mv', 'copy', 'move'), 'ERROR: Invalid copy or move command type ({0})'.format(command)
    command = 'mv' if command == 'mv' or command == 'move' else 'cp'

    cmd = 'aws s3 {command} {uri1} {uri2}'
    cmd += ' --quiet' if quiet else ''
    cmd += ' --acl {acl}'
    cmd += ' --recursive' if recursive else ''
    cmd += ' --include "{0}"'.format(include) if include else ''
    cmd += ' --exclude "{0}"'.format(exclude) if exclude else ''
    return cmd.format(command=command, uri1=clean_path(object1), uri2=clean_path(object2), acl=acl)


class S3Commands:
    @staticmethod
    def list(uri='', recursive=False, human_readable=False, summarize=False):
        """
        List files/folders in a bucket if a URI is specified or list available buckets.

        :param uri: S3 bucket URI
        :param recursive: Recursively list files/folders
        :param human_readable: Displays file sizes in human readable format
        :param summarize: Displays summary information (number of objects, total size)
        :return: Command string
        """
        cmd = 'aws s3 ls {uri}'
        cmd += ' --recursive' if recursive else ''
        cmd += ' --human-readable' if human_readable else ''
        cmd += ' --summarize' if summarize else ''
        return cmd.format(uri=uri)

    @staticmethod
    def copy(object1, object2, recursive=False, include=None, exclude=None, acl='private', quiet=True):
        """Copy file(s)/folder(s) from one S3 bucket location to another. See move_or_copy for more."""
        return move_or_copy('cp', object1, object2, recursive, include, exclude, acl, quiet)

    @staticmethod
    def move(object1, object2, recursive=False, include=None, exclude=None, acl='private'):
        """Move file(s)/folder(s) from one S3 bucket location to another. See move_or_copy for more."""
        return move_or_copy('mv', object1, object2, recursive, include, exclude, acl)

    @staticmethod
    def remove(uri, recursive=False, include=None, exclude=None):
        """
        Delete an S3 object from a bucket.

        :param uri: S3 object uri
        :param recursive: Recursively copy all files within the directory
        :param include: Don't exclude files or objects in the command that match the specified pattern
        :param exclude: Exclude all files or objects from the command that matches the specified pattern
        :return: Command string
        """
        cmd = 'aws s3 rm {uri}'
        cmd += ' --recursive' if recursive else ''
        cmd += ' --exclude "{0}"'.format(exclude) if exclude else ''
        cmd += ' --include "{0}"'.format(include) if include else ''
        return cmd.format(uri=clean_path(uri))

    @staticmethod
    def sync(source, destination, delete=False, acl='private', quiet=False):
        """
        Synchronize local files with an S3 bucket.

        :param source: Local source directory or S3 URI
        :param destination: Local source or URI of destination S3 bucket (with path)
        :param delete: Sync with deletion, disabled by default
        :param acl: Access permissions, must be either 'private', 'public-read' or 'public-read-write'
        :param quiet: When true, does not display the operations performed from the specified command
        :return: Command string
        """
        cmd = 'aws s3 sync {source_path} {destination_uri}'
        cmd += ' --acl {acl}'
        cmd += ' --quiet' if quiet else ''
        cmd += ' --delete' if delete else ''
        return cmd.format(source_path=clean_path(source), destination_uri=clean_path(destination), acl=acl)

    @staticmethod
    def make_bucket(uri, region=None):
        """
        Creates an S3 bucket.

        :param uri: S3 bucket uri
        :param region: AWS region
        :return: Command string
        """
        cmd = 'aws s3 mb {uri}'
        cmd += ' --region {region}'.format(region=region) if region else ''
        return cmd.format(uri=clean_path(uri))

    @staticmethod
    def remove_bucket(uri, force=False):
        """
        Delete an S3 bucket if it is empty.

        :param uri: S3 bucket uri
        :param force: Deletes all objects in the bucket including the bucket itself
        :return: Command string
        """
        cmd = 'aws s3 rb {uri}'
        cmd += ' --force' if force else ''
        return cmd.format(uri=clean_path(uri))

    @staticmethod
    def pre_sign(uri, expiration=3600):
        """
        Generate a pre-signed URL for an Amazon S3 object.

        This allows anyone who receives the pre-signed URL to retrieve the S3 object
        with an HTTP GET request.

        :param uri: S3 object URI
        :param expiration: Number of seconds until the pre-signed URL expires
        :return: Command string
        """
        return 'aws s3 presign {uri} --expires-in {expiration}'.format(uri=clean_path(uri), expiration=expiration)
