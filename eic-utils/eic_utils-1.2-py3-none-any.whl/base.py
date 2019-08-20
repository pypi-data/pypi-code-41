import os, time
def get_cur_time():
    """ return time in format '%Y/%m/%d %H:%M:%s' """
    return time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())

def touch_suffix(target, suffix):
    """ add 'prefix' to 'target' if 'target' is not start with 'suffix' """
    return target + ('' if target.endswith(suffix) else suffix)

def touch_prefix(target, prefix):
    """ append 'suffix' to 'target' if 'target' is not end with 'suffix' """
    return ('' if target.startswith(prefix) else prefix) + target

def file_type(path):
    """
        Args:
            path (str): path to query
    
        Return:
            file type (str): one of ['dir', 'file', 'link', None]
    """
    if os.path.isdir(path):
        return 'dir'
    if os.path.isfile(path):
        return 'file'
    if os.path.islink(path):
        return 'link'
    return None

if __name__ == '__main__':
    print(get_cur_time())
    print(touch_prefix('hi', 'as'))
    print(touch_suffix('hi', 'as'))
