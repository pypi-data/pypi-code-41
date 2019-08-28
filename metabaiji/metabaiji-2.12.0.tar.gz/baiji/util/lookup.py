def get_versioned_key_remote(bucket, key_name, version_id=None):
    '''
    Utility function to get versioned key from a bucket

    '''
    from boto.exception import S3ResponseError
    from baiji.exceptions import InvalidVersionID

    key = None
    try:
        key = bucket.get_key(key_name, version_id=version_id)
    except S3ResponseError as e:
        if e.status == 400:
            raise InvalidVersionID("Invalid versionID %s" % version_id)
        else:
            raise
    return key
