import os, random, datetime, uuid

def set_path(path):
    path = path.replace("\\", "/")
    if path[0] != '/' and path[1] != ':':
        path = os.getcwd().replace("\\", "/") + "/" + path
    return path

def folder(path):
    path = set_path(path)
    if path[-1] == '/':
        path = path[0:len(path)-1]
    try:
        if os.path.isdir(path) is False:
            os.mkdir(path)
    except Exception as e:
        print("create Folder : ", e)
        repath = str(path).split("/")[-1]
        repath = str(path).split("/"+repath)[0]
        folder(repath)
        folder(path)
    if path[-1] is not '/':
        path = path+"/"
    return path

def colors(n):
    colors = []
    for _ in range(n + 1):
        _color = (random.randrange(0, 256), random.randrange(0, 256), random.randrange(0, 256))
        colors.append(_color)
    return colors

def name(file_format, path=None):
    if file_format[0] != '.':
        file_format="."+file_format
    file_name = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_name = file_name.replace(":", "").replace(" ", "").replace("-", "")
    if path:
        if os.path.isfile(path+file_name):
            return name(file_format, path)
    return file_name + uuid.uuid4().hex + file_format