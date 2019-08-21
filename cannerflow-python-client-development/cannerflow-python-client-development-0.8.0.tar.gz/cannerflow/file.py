import requests
from cannerflow.csv_wrapper import CsvWrapper
from cannerflow.json_wrapper import JsonWrapper
from cannerflow.image_wrapper import ImageWrapper
__all__ = ["File"]

class File(object):
    def __init__(
        self,
        workspaceId,
        request,
        replaceLocalhostString
    ):
        self.workspaceId = workspaceId
        self.request = request
        self.replaceLocalhostString = replaceLocalhostString
    def getPayload(self):
        return {
            'operationName': 'files',
            'query': """
                query files($where: FileWhereInput!, $recursive: Boolean) {
                    files(where: $where, recursive: $recursive) {
                        name
                        absolutePath
                        size
                        isFolder
                        lastModified
                        wiki
                    }
                }
            """,
            'variables': {
                'where': {
                    'workspaceId': self.workspaceId
                },
                'recursive': False
            }
        }
    def fetch(self):
        return self.request.post(self.getPayload()).get('files')
    def list_absolute_path(self):
        data = self.fetch()
        return list(map(lambda x: '/' + x['absolutePath'], data))
    def _replace_localhost(self, url):
        if (self.replaceLocalhostString != None):
            return url.replace('localhost', self.replaceLocalhostString).replace('127.0.0.1', self.replaceLocalhostString)
        else:
            return url;
    def _get_download_signed_url(self, absolutePath):
        objectName = absolutePath;
        if (absolutePath[0] == '/'):
            objectName = absolutePath[1:]
        data = self.request.get(f'api/getSignedUrl?workspaceId={self.workspaceId}&objectName={objectName}')
        return data
    def _get(self, absolutePath):
        data = self._get_download_signed_url(absolutePath)
        # quick fix: in notebook we can't get minio data from localhost
        url = self._replace_localhost(data['signedUrl'])
        http_response = {}
        try:
            http_response = requests.get(url)
            http_response.raise_for_status()
        except Exception as err:
            content = http_response.get('content')
            print(f'Error occured: {err}, {content}')
        else:
            return http_response
    def get_content(self, absolutePath):
        r = self._get(absolutePath)
        return r.content
    def get_text(self, absolutePath):
        r = self._get(absolutePath)
        r.encoding = 'utf-8'
        return r.text
    def get_csv_wrapper(self, absolutePath):
        content = self.get_content(absolutePath)
        csvWrapper = CsvWrapper(content=content)
        return csvWrapper
    def get_json_wrapper(self, absolutePath):
        content = self.get_content(absolutePath)
        jsonWrapper = JsonWrapper(content=content)
        return jsonWrapper
    def get_image_wrapper(self, absolutePath):
        content = self.get_content(absolutePath)
        imageWrapper = ImageWrapper(content=content)
        return imageWrapper

