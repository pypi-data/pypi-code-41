import os
def filelines(full_filename):
    """
    Quickly returns the number of lines in a file.
    Returns None if an error is raised.
    """
    with open(full_filename, 'r') as file:
        return sum(1 for line in file)
    return None

def slices(arr, slcs):
    '''
    Args:
        arr (list): a list of elements.
        slcs (list): a list of slice specifications.

    Returns:
        (list): A list of elements extracted from arr given all slcs.
    '''
    return [col for slc in slcs for col in arr[slc]]

def linesplit(line, delim='\t', newline='\n'):
    '''
    Args:
        line (str): a line in a file
    Kwargs:
        delim (str): Defaults to '\t'.
        newline (str): Defaults to '\n'

    Returns:
        (str): the line split and devoid of newline.
    '''
    return line.rstrip(newline).split(delim)

def linemend(line, delim='\t', newline='\n'):
    '''
    Args:
        line (str): a line in a file
    Kwargs:
        delim (str): Defaults to '\t'.
        newline (str): Defaults to '\n'

    Returns:
        (str): the line joined and given a newline. (opposite of linesplit)
    '''
    return delim.join(line)+newline

def readsplit(file_object, delim='\t', newline='\n'):
    '''
    Args:
        file_object (file object): an opened file
    Kwargs:
        delim (str): Defaults to '\t'.
        newline (str): Defaults to '\n'

    Returns:
        (str): Calls linesplit on file_object.readline()
    '''
    return linesplit(file_object.readline(), delim, newline)

def readslice(file_object, slcs, delim='\t', newline='\n', add_newline_q=True):
    '''
    Args:
        file_object (file object): an opened file
        slcs (list):a list of slice specifications.
    Kwargs:
        delim (str): Defaults to '\t'.
        newline (str): Defaults to '\n'
        add_newline_q (bool): Defaults to True

    Returns:
        (str): Reads the line, splits it by slice, and then joins it back together.
    '''
    return delim.join(slices(readsplit(file_object, delim, newline), slcs)) \
    + (newline if add_newline_q else '')

def lineslice(line, slcs, delim='\t', newline='\n', add_newline_q=True):
    '''
    Args:
        line (str): a line in a file
        slcs (list):a list of slice specifications.
    Kwargs:
        delim (str): Defaults to '\t'.
        newline (str): Defaults to '\n'
        add_newline_q (bool): Defaults to True

    Returns:
        (str): Reads the line, splits it by slice, and then joins it back together.
    '''
    return delim.join(slices(linesplit(line, delim, newline), slcs)) \
    + (newline if add_newline_q else '')


def superdirs(location, up_to):
    '''
    Args:
        location (str): a full path.
        up_to (str): a sub-specficiation of full path. e.g. root --> dir_x
            where full path is: /dir_1/.../dir_x/.../dir_n
    Returns:
        (list): list of directories that come after up_to in location
    '''
    relative_path = location.replace(up_to, '').lstrip('/')
    sups = list(filter(lambda s: s is not '', relative_path.split('/')))
    return sups


def sharddir(location, up_to):
    '''
    Args:
        location (str): a full path.
        up_to (str): a sub-specficiation of full path. e.g. root --> dir_x
            where full path is: /dir_1/.../dir_x/.../dir_n
    Returns:
        (str): all the directories prior to up_to (dir_x)
    '''
    supdirs = os.path.join(*superdirs(location, up_to))
    return location.replace(supdirs, '').rstrip('/')

def shardname(location, up_to):
    '''
    Args:
        location (str): a full path.
        up_to (str): a sub-specficiation of full path. e.g. root --> dir_x
            where full path is: /dir_1/.../dir_x/.../dir_n
    Returns:
        (str): the name of the directory prior to up_to (dir_x).
    '''
    return os.path.basename(sharddir(location, up_to))

def shardloc(location, up_to):
    '''
    Args:
        location (str): a full path.
        up_to (str): a sub-specficiation of full path. e.g. root --> dir_x
            where full path is: /dir_1/.../dir_x/.../dir_n
    Returns:
        (str): the name of the directory prior to up_to (dir_x).
    '''
    return os.path.dirname(sharddir(location, up_to))




def readlines_split(file, delim='\t', newline='\n'):

    lines = []
    with open(file, 'r') as f:
        for line in f:
            lines.append(linesplit(line, delim, newline))
    return lines


def dir_from_cols(fields, cols):
    '''
    Args:
        fields (list): elements in a record.
        cols (list): list of column indicies to take.

    Returns:
        (str): the directory produced by taking fields[cols[i]] for each column.
            e.g. fields[cols[0]]/.../fields[cols[n]]
    '''
    return os.path.join(*[fields[i] for i in cols])
