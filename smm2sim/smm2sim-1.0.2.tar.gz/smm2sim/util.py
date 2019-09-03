playoff_series_ids = {
    ('A', 1):('A','Division Quarterfinals',1),
    ('A', 2):('A','Division Quarterfinals',2),
    ('A', 3):('A','Division Quarterfinals',3),
    ('A', 4):('A','Division Quarterfinals',4),
    ('A', 5):('A','Division Semifinals',1),
    ('A', 6):('A','Division Semifinals',2),
    ('A', 7):('A','Division Finals',1),
    ('B', 1):('B','Division Quarterfinals',1),
    ('B', 2):('B','Division Quarterfinals',2),
    ('B', 3):('B','Division Quarterfinals',3),
    ('B', 4):('B','Division Quarterfinals',4),
    ('B', 5):('B','Division Semifinals',1),
    ('B', 6):('B','Division Semifinals',2),
    ('B', 7):('B','Division Finals',1)}

def extractText(tosearch, delim_left='', delim_right= None,
                reverse_left=False, reverse_right=False,
                optional_left=False, optional_right=False):
    rdelim = delim_left if delim_right is None else delim_right
    returnval = tosearch
    if delim_left != '':
        returnval = extractHelper(returnval, delim_left, reverse_left, optional_left, True)
    if rdelim != '':
        returnval = extractHelper(returnval, rdelim, reverse_right, optional_right, False)
    return returnval

def extractHelper(tosearch, delim, reverse_order, is_optional, is_left):
    cond1 = (is_left == (is_optional == reverse_order))
    cond2 = (not reverse_order) and is_left
    n = 2 if is_left else 0
    basefunc = str.rpartition if reverse_order else str.partition
    partitioned = basefunc(tosearch, delim)
    return partitioned[n] if (cond1 or partitioned[1] == delim) else partitioned[0] if cond2 else ''