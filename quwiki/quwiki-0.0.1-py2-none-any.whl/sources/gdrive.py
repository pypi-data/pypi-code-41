import re
import io
import pickle
import base64
import zipfile
import pathlib
import os.path
from io import BytesIO
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from apiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from quwiki.filenode import FileNode


SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
FILE_TOKEN_PATTERN = 'secrets/token.pickle'


class GdriveFileNode(FileNode):
    def __init__(self, gdrive_id, name, kind, gservice):
        FileNode.__init__(self, name=name, kind=kind)
        self.gservice = gservice
        self.gdrive_id = gdrive_id
        self._html = None

    def get_html(self):
        if self._html:
            return self._html

        request = self.gservice.files().export_media(fileId=self.gdrive_id, mimeType='application/zip')
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        zip_file = fh.getvalue()

        zipdata = BytesIO()
        zipdata.write(zip_file)
        myzipfile = zipfile.ZipFile(zipdata)

        html = myzipfile.open(myzipfile.filelist[0].filename).read().decode('UTF-8')

        soup = BeautifulSoup(html, "html.parser")

        imgs = soup.find_all('img')
        for img in imgs:
            img_src = img.attrs['src']

            byte_like_img = myzipfile.open(img_src).read()
            data_uri = base64.b64encode(byte_like_img).decode('utf-8')
            
            img.attrs['src'] = f"data:image/png;base64,{data_uri}"

        html_body = ''.join([content.prettify() for content in soup.find('body').contents])
        self._html = html_body
        return self._html

    def get_edit_url(self):
        return 'https://docs.google.com/document/d/{}/edit'.format(self.gdrive_id)


def _get_gservice(pickle_file):
    creds = None
    with open(pickle_file, 'rb') as token:
        creds = pickle.load(token)
    service = build('drive', 'v3', credentials=creds)
    return service


def _populate_tree(root):
    queue = [ root ]
    gservice = root.gservice

    while len(queue) > 0:
        parent_file_node = queue.pop()
        query = '"{}" in parents and trashed=false'.format(parent_file_node.gdrive_id)
        results = gservice.files().list(q=query).execute()
        items = results.get('files')

        for item in items:
            kind = None
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                kind = FileNode.KIND_DIRECTORY
            elif item['mimeType'] == 'application/vnd.google-apps.document':
                kind = FileNode.KIND_FILE
            else:
                # Filetype is not supported
                pass

            if kind:
                file_node = GdriveFileNode(
                    gdrive_id=item['id'],
                    name=item['name'],
                    kind=kind,
                    gservice=gservice
                )
                parent_file_node.add_child(file_node)
                if kind == FileNode.KIND_DIRECTORY:
                    queue.append(file_node)
    return root


def _get_folder_id_from_url(url):
    # TODO: Check if ID length is constant and equal to 33
    res = re.findall(r'.*\/([A-Za-z0-9]{33})', url)
    return res[0]


def generate_tree(source):
    gservice = _get_gservice(source['token'])
    folder_id = _get_folder_id_from_url(source['url'])

    root = GdriveFileNode(
        gdrive_id=folder_id,
        name=source['title'],
        kind=FileNode.KIND_DIRECTORY,
        gservice=gservice
    )
    _populate_tree(root)

    return root


def initialize(config):
    print('GDrive | In order allow access to Google Drive you need to download `credentials.json` file from Google')
    print('GDrive | Please visit https://developers.google.com/drive/api/v3/quickstart/python, click ENABLE THE DRIVE API and DOWNLOAD CLIENT CONFIGURATION')

    # Require `credentials.json` file
    file_secrets = ''
    while not os.path.exists(file_secrets):
        file_secrets = input('GDrive | Please enter file path to `credentials.json`: ')

    # Obtain credentials
    flow = InstalledAppFlow.from_client_secrets_file(file_secrets, SCOPES)
    creds = flow.run_local_server(port=0)

    # Store tocket to `.pickle` file
    pathlib.Path('secrets').mkdir(parents=True, exist_ok=True)
    file_token = FILE_TOKEN_PATTERN
    counter = 1
    while os.path.exists(file_token):
        file_token = FILE_TOKEN_PATTERN
        base, extension = file_token.split('.')
        base += '_' + str(counter)
        file_token = '.'.join([base, extension])
        counter += 1

    with open(file_token, 'wb') as token:
        pickle.dump(creds, token)

    # Obtain folder URL
    folder_url_valid = False
    while not folder_url_valid:
        folder_url = input('GDrive | URL of Google Drive folder: ')
        try:
            _get_folder_id_from_url(folder_url)
            folder_url_valid = True
        except Exception:
            print('GDrive | Invalid Google Drive folder URL')

    print('GDrive | Conragts! The authentification is successful.')
    print('GDrive | The token is stored to: ', file_token)

    config['url'] = folder_url
    config['token'] = file_token

    return config