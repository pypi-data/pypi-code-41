import os
from git import Repo
from tempfile import gettempdir
import markdown
from quwiki.filenode import FileNode
from pathlib import Path
from bs4 import BeautifulSoup
import base64


class GitFileNode(FileNode):
    def __init__(self, name, kind, localpath, url):
        FileNode.__init__(self, name=name, kind=kind)
        self.localpath = localpath
        self.url = url

    def get_html(self):
        md = ''
        if os.path.isfile(self.localpath):
            md = open(self.localpath, 'r').read()            

        html = markdown.markdown(md, extensions=['tables'])

        # find all image src and replace with base64
        soup = BeautifulSoup(html, 'html.parser')
        imgs = soup.find_all('img')
        
        for img in imgs:
            img_src = img.attrs['src']

            img_src_path = os.path.join(os.path.dirname(self.localpath), img_src)
            byte_like_img = open(img_src_path, 'rb').read()
            data_uri = base64.b64encode(byte_like_img).decode('utf-8')

            img.attrs['src'] = 'data:image/png;base64,{}'.format(data_uri)

        return soup.prettify()

    def get_edit_url(self):
        return self.url


def _populate_tree(root):
    queue = [ root ]

    while len(queue) > 0:
        parent_file_node = queue.pop()
        items = os.listdir(parent_file_node.localpath)

        for item in items:
            kind = None
            localpath = os.path.join(parent_file_node.localpath, item)
            if os.path.isdir(localpath):
                kind = FileNode.KIND_DIRECTORY
            elif Path(localpath).suffix == '.md':
                kind = FileNode.KIND_FILE
            else:
                # Filetype is not supported
                pass

            if kind:
                file_node = GitFileNode(
                    name=item,
                    kind=kind,
                    localpath=localpath,
                    url=parent_file_node.url
                )
                parent_file_node.add_child(file_node)
                if kind == FileNode.KIND_DIRECTORY:
                    queue.append(file_node)
    return root


def generate_tree(source):
    subfolder = source['directory'] if 'directory' in source else ''

    tmp = os.path.join(gettempdir(), '.{}'.format(hash(os.times())))
    Repo.clone_from(source['url'], tmp, depth=1)
    md_folder = os.path.join(tmp, subfolder)

    root = GitFileNode(
        name=source['title'],
        kind=FileNode.KIND_DIRECTORY,
        localpath=md_folder,
        url=source['url']
    )
    _populate_tree(root)
    return root


def initialize(config):
    config['url'] = None
    config['path'] = ''

    # Obtain Git URL
    url_valid = False
    config['url'] = None
    while not url_valid:
        config['url'] = input('Git | URL of Git repo: ')
        try:
            url_valid = True
        except Exception:
            print('Git | Invalid Git repo URL')

    # Obtain path
    config['directory'] = input('Git | Path in repo to documentation []: ')

    return config