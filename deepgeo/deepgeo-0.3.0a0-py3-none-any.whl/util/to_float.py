def __check__(o):
    o = str(o)
    try:
        o=int(o)
    except:
        try:
            o=float(o)
        except:
            pass
    return o

def __string__(o):
    nums = str(o).split("/")
    a = float(nums[0])
    b = float(nums[1])
    if a==0 or b==0:
        return float(0)
    return a/b

def __int__(o):
    return float(str(o))

def __float__(o):
    return o

def to_float(o):
    o = __check__(o)
    if isinstance(o, int):
        return __int__(o)
    elif isinstance(o, float):
        return __float__(o)
    else:
        return __string__(o)