from . import create
import http.client as httplib
import shutil

def parse(url):
    domain = url.split("/")[0]
    get = url.split(domain)[-1]
    return domain, get

def get_page(protocol, domain, get):
    conn = None
    if protocol == "https":
        conn = httplib.HTTPSConnection(domain)
    elif protocol == "http":
        conn = httplib.HTTPConnection(domain)
    if conn is not None:
        conn.request("GET", get)
        page = conn.getresponse()
        return page.read()
    else:
        return None

def copy(from_path, to_path):
    shutil.copy(from_path, to_path)

def download(url, to_path, ext_list):
    protocol = url.split("://")
    file_ext = url.split(".")[-1]
    if file_ext in ext_list:
        file_name = create.name(file_ext)
    else:
        file_name = create.name(ext_list[0])
    if 'http' in protocol[0] or 'https' in protocol[0]:
        domain, get = parse(protocol[1])
        page = get_page(protocol[0], domain, get)
        if page is not None:
            fail = open(to_path + file_name, "wb")
            fail.write(page)
            fail.close()
            r_url = file_name
        else:
            r_url = None
    elif 'file' in protocol[0]:
        try:
            copy(protocol[1], to_path + file_name)
            r_url = file_name
        except Exception as e:
            print(str(e) + " Error")
            r_url = None
    else:
        r_url = url
    return r_url

def download_video(url, to_path):
    return download(url, to_path, ['mp4', 'MP4', 'avi', 'AVI', 'mkv', 'MKV'])

def download_image(url, to_path):
    return download(url, to_path, ['jpg', 'JPG', 'png', 'PNG', 'gif', 'GIF', 'bmp', 'BMP'])