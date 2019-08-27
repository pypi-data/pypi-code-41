def _strip_initial_slashes(key):
    '''
    Keys going into boto need to not have initial slashes.
    '''
    import re
    return re.sub(r'^/*', '', key)
