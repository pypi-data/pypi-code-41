import os
from argparse import ArgumentParser

from awsutils.s3.s3 import S3, bucket_uri


def print_output(event, bucket=None, local_path=None, remote_path=None):
    string = '{0}: {1} => {2}' if not event.lower().startswith('download') else '{0}: {2} to {1}'
    print(string.format(event, local_path, os.path.join(bucket_uri(bucket), remote_path if remote_path else '')))


def upload(bucket=None, local_path=None, remote_path=None):
    """Upload a file or folder to an AWS S3 bucket."""
    S3(str(bucket), quiet=False).upload(local_path=local_path, remote_path=remote_path)


def download(bucket=None, local_path=None, remote_path=None, recursive=False):
    """Download a file or folder to an AWS S3 bucket."""
    S3(str(bucket), quiet=False).download(local_path=local_path, remote_path=remote_path, recursive=recursive)


def sync(bucket=None, local_path=None, remote_path=None, delete=False, remote_source=False):
    """Sync files or folders to an AWS S3 bucket."""
    S3(str(bucket), quiet=False).sync(local_path=local_path, remote_path=remote_path, delete=delete,
                                      remote_source=remote_source)


def main():
    # Declare argparse argument descriptions
    usage = 'AWS S3 command-line-interface wrapper.'
    description = 'Execute AWS S3 commands.'
    helpers = {
        'bucket': "AWS S3 bucket name.",
    }

    # construct the argument parse and parse the arguments
    parser = ArgumentParser(usage=usage, description=description)
    sub_parser = parser.add_subparsers()

    # Upload
    parser_upload = sub_parser.add_parser('upload')
    parser_upload.add_argument('--bucket', help=helpers['bucket'], type=str)
    parser_upload.add_argument('--local_path', type=str)
    parser_upload.add_argument('--remote_path', type=str)
    parser_upload.set_defaults(func=upload)

    # Download
    parser_download = sub_parser.add_parser('download')
    parser_download.add_argument('--bucket', help=helpers['bucket'], type=str)
    parser_download.add_argument('--local_path', type=str)
    parser_download.add_argument('--remote_path', type=str)
    parser_download.add_argument('--recursive', action='store_true', default=False)
    parser_download.set_defaults(func=download)

    # Sync
    parser_sync = sub_parser.add_parser('sync')
    parser_sync.add_argument('--bucket', help=helpers['bucket'], type=str)
    parser_sync.add_argument('--local_path', type=str)
    parser_sync.add_argument('--remote_path', type=str, default=None)
    parser_sync.add_argument('--delete', action='store_true', default=False)
    parser_sync.add_argument('--remote_source', action='store_true', default=False)
    parser_sync.set_defaults(func=sync)

    # Parse Arguments
    args = vars(parser.parse_args())
    func = args.pop('func')
    func(**args)


if __name__ == '__main__':
    main()
