
def pad(thelist, size, padding):
    if len(thelist) < size:
        for _ in range(size - len(thelist)):
            thelist.append(padding)
    return thelist

def chunk(thelist, size, with_padding=False, padding=None):
    data = []
    start = 0
    while True:
        if len(thelist) < size:
            if with_padding:
                pad(thelist, size, padding)
            data.append(thelist)
            break
        data.append(thelist[start:start+size])
        thelist = thelist[start+size:]
        if not thelist:
            break
    return data

def clean_none(thelist):
    """Remove None or empty element in thelist.
    """
    return [value for value in thelist if value]
