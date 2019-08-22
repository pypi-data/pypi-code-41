# -*- coding: utf-8 -*-
import hashlib


def get_key_from_path_and_site(path, site_id):
    '''
    cache key has to be < 250 chars to avoid memcache.Client.MemcachedKeyLengthError
    The best algoritm is SHA-224 whose output (224 chars) respects this limitations
    '''
    key = '{}_{}'.format(path, site_id)
    key = hashlib.sha224(key.encode('utf-8')).hexdigest()
    return key
