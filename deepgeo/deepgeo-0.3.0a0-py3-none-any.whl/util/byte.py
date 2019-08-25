def count(o):
    bytes_ = str(o.encode()).replace("b'","")
    count = 0
    pass_ = 0
    for byte in bytes_:
        if pass_!=0:
            pass_-=1
            continue
        if byte == '\\':
            pass_=11
            count+=1
        count+=1
    return count -1