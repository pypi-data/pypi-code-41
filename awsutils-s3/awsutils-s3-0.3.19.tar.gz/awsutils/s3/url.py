from urllib.parse import urlparse

from tldextract import extract as url_extract
from validators import url as url_validator


def url_host(url):
    """
    Retrieve the 'hostname' of a url by parsing its contents

    :param url: URL
    :return: hostname
    """
    return '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))


def bucket_uri(bucket):
    """
    Convert a S3 bucket name string in to a S3 bucket uri.

    :param bucket: Bucket name
    :return: Bucket URI
    """
    return 's3://{bucket}'.format(bucket=bucket)


def bucket_url(bucket, acceleration=True):
    """
    Convert a S3 bucket name string in to a S3 bucket url.

    :param bucket: Bucket name
    :param acceleration: Use transfer acceleration if the endpoint is available
    :return: Bucket URL
    """
    url = 'https://{bucket}.s3.amazonaws.com'.format(bucket=bucket)
    url_accel = 'https://{bucket}.s3-accelerate.amazonaws.com'.format(bucket=bucket)
    return url_accel if url_validator(url_accel) and acceleration else url


def bucket_name(url):
    """
    Retrieve an AWS S3 bucket name from a URL.

    :param url: URL
    :return: Bucket name
    """
    result = url_extract(url)
    if result.subdomain == 's3':
        return url.replace(url_host(url), '').split('/')[0]
    else:
        return result.subdomain.replace('.s3-accelerate', '').replace('.s3', '')


def key_extract(url):
    """
    Retrieve an AWS object key from a URL.

    :param url: URL
    :return: Object key
    """
    result = url_extract(url)
    if result.subdomain == 's3':
        return url.replace(url_host(url), '').split('/', 1)[-1]
    else:
        return url.replace(url_host(url), '')
