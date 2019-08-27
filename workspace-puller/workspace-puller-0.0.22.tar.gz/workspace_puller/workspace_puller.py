import datetime
import json
import tempfile

import certifi
import yaml
import io
import os
from git import Repo
import shutil
import urllib3
import requests

from oauth2client.client import OOB_CALLBACK_URN
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from downloader import Download
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from workspace_puller import tools as t
from workspace_puller.wp_telegram_bot import WPTelegramBot


class WorkspacePuller:

    def __init__(self, config_url: str, telegram_token=None):
        self.kaggle_dirmode = 'skip'
        config_file_name = 'config_' + str(
            datetime.datetime.now()) + '.yml'
        self.download_config(config_url, config_file_name)
        self.config = WorkspaceConfig(
            self.parse_config(config_file_name))
        os.remove(config_file_name)
        self.pool_manager = urllib3.PoolManager(
            num_pools=1,
            maxsize=1,
            cert_reqs='CERT_REQUIRED',
            ca_certs=certifi.where()
        )
        self.telegram_bot = None
        if telegram_token is not None:
            self.telegram_bot = WPTelegramBot(token=telegram_token, chat_ids=self.config.telegram_channels)

    def build_workspace(self):
        if self.config is None:
            return
        self.gauth = self.get_gauth()
        if self.config.dataset_list is not None:
            self.download_list(self.config.dataset_list)
        if self.config.repos is not None:
            self.clone_repos(self.config.repos)
        if self.config.script_files is not None:
            self.run(self.config.script_files)
        if self.config.gdrive_folders is not None:
            self.send_output_to_gdrive(self.config.output_folder, self.config.gdrive_folders)
        if self.config.kaggle is not None:
            self.upload_data_to_kaggle()
            if 'dirmode' in self.config.kaggle:
                self.kaggle_dirmode = self.config.kaggle['dirmode']
        t.log_message('Done.')
        if self.telegram_bot is not None:
            self.telegram_bot.send_message('Workspace build done.')

    def get_gauth(self):
        gauth = None
        packge_path, _ = os.path.split(__file__)
        client_config = os.path.join(packge_path, 'client_secrets.json')
        credentials_file = os.path.join(packge_path, 'drive_credentials')
        if os.path.exists(credentials_file):
            try:
                gauth = GoogleAuth()
                gauth.LoadClientConfigFile(client_config_file=client_config)
                gauth.LoadCredentialsFile(credentials_file=credentials_file)
                return gauth
            except Exception as e:
                t.log_message(str(e))
                gauth = None
        if self.config.gdrive_folders is not None and self.config.telegram_channels is not None and self.telegram_bot is not None:
            try:
                gauth = self.start_auth_telegram(client_config=client_config)
                gauth.SaveCredentialsFile(credentials_file=credentials_file)
            except Exception as e:
                t.log_message(str(e))
                gauth = None
        elif self.config.gdrive_folders is not None and self.telegram_bot is None or self.config.telegram_channels is None:
            try:
                gauth = GoogleAuth()
                gauth.LoadClientConfigFile(client_config_file=client_config)
                gauth.CommandLineAuth()
                gauth.SaveCredentialsFile(credentials_file=credentials_file)
            except Exception as e:
                t.log_message(str(e))
                gauth = None
        return gauth

    def download_config(self, config_url: str, file_name: str = None):
        downloader = Download(config_url, file_name)
        downloader.download()

    def parse_config(self, config_file_path):
        stream = io.open(config_file_path, mode='r', buffering=-1, encoding=None, errors=None, newline=None,
                         closefd=True)
        yml = yaml.load(stream=stream, Loader=yaml.CLoader)
        return yml

    def run(self, run_file_list: list):
        for item in run_file_list:
            if not os.path.exists(item):
                t.log_message('ERROR. File not found: ' + item)
                continue
            t.log_message("Executing file: " + item)
            os.system('python ' + item)

    def download_list(self, url_list: list):
        for item in url_list:
            t.log_message('Downloading: ' + item)
            try:
                download = Download(item, retries=5)
                download.download()
                path = os.path.abspath(download.download_path)
                _, extension = os.path.splitext(path)
                if extension[1:] in dict(shutil.get_archive_formats()).keys() and self.config.extract_archives:
                    shutil.unpack_archive(path)
            except Exception as e:
                t.log_message("ERROR. Download: " + item + ' FAILED.\n' + str(e))

    def clone_repos(self, repos: dict):
        for repo_name, repo_data in repos.items():
            branch: str = None
            if 'branch' in repo_data:
                branch = repo_data['branch']
            if 'url' in repo_data:
                url: str = repo_data['url']
                if os.path.exists(repo_name):
                    shutil.rmtree(repo_name)
                if branch is not None:
                    t.log_message('Cloning repo: ' + url + ', branch: ' + branch + ', to the folder: ' + repo_name)
                    Repo.clone_from(url=url, to_path=repo_name, branch=branch)
                else:
                    t.log_message('Cloning repo: ' + url + ', to the folder: ' + repo_name)
                    Repo.clone_from(url=url, to_path=repo_name)
            else:
                t.log_message('ERROR. URL not found for a repo: ' + repo_name)

    def send_output_to_gdrive(self, output_folders: list, drive_folders: list):
        if self.gauth is None and self.config.gdrive_folders is not None:
            t.log_message('GoogleDrive is unauthorised. Upload canceled.')
            return
        drive = GoogleDrive(self.gauth)
        t.log_message('Uploading an output folders to the Google Drive')
        for drive_folder in drive_folders:
            for folder in output_folders:
                self.upload_to_drive(folder, drive_folder, drive)

    def upload_to_drive(self, folder: str, drive_folder_id: str, drive: GoogleDrive):
        title: str = os.path.basename(folder)
        if not os.path.isdir(folder):
            file_metadata = {
                "title": title,
                "parents": [
                    {
                        "kind": "drive#fileLink",
                        "id": drive_folder_id
                    }
                ]
            }
            file = drive.CreateFile(file_metadata)
            file.SetContentFile(folder)
            file.Upload()
        else:
            folder_metadata = {
                'title': title,
                'mimeType': 'application/vnd.google-apps.folder',
                "parents": [
                    {
                        "kind": "drive#fileLink",
                        "id": drive_folder_id
                    }
                ]
            }
            dirve_folder = drive.CreateFile(folder_metadata)
            dirve_folder.Upload()
            for item in os.listdir(folder):
                path = os.path.join(folder, item)
                self.upload_to_drive(path, dirve_folder['id'], drive)

    def start_auth_telegram(self, client_config):
        if self.telegram_bot is None:
            t.log_message('telegram bot is None. Telegram auth canceled.')
            return
        auth = GoogleAuth()
        auth.LoadClientConfigFile(client_config_file=client_config)
        if auth.flow is None:
            auth.GetFlow()
        auth.flow.redirect_uri = OOB_CALLBACK_URN
        self.telegram_bot.send_message(
            'Please go to the following link in your browser and send me a Google verification code. \nAuth url: ' + auth.GetAuthUrl())
        dirty = False
        code = None
        save_credentials = auth.settings.get('save_credentials')
        if auth.credentials is None and save_credentials:
            auth.LoadCredentials()
        if auth.credentials is None:
            code = self.telegram_bot.get_code()
            dirty = True
        else:
            if auth.access_token_expired:
                if auth.credentials.refresh_token is not None:
                    auth.Refresh()
                else:
                    code = self.telegram_bot.get_code()
                dirty = True
        if code is not None:
            auth.Auth(code)
        if dirty and save_credentials:
            auth.SaveCredentials()
        return auth

    def upload_data_to_kaggle(self):
        files = []
        for output_folder in self.config.output_folder:
            t.log_message('Uploading an output folder to the Kaggle: ' + output_folder)
            for item in os.listdir(output_folder):
                path = os.path.join(output_folder, item)
                if os.path.isfile(path):
                    token = self.upload_file_to_kaggle(path)
                    files.append({'token': token})
                elif os.path.isdir(path) and self.kaggle_dirmode in ['zip', 'tar']:
                    temp_dir = tempfile.mkdtemp()
                    try:
                        _, dir_name = os.path.split(path)
                        archive_path = shutil.make_archive(
                            os.path.join(temp_dir, dir_name), self.kaggle_dirmode,
                            path)
                        token = self.upload_file_to_kaggle(archive_path)
                        files.append({'token': token})
                    finally:
                        shutil.rmtree(temp_dir)
            t.log_message(output_folder + ' - uploaded.')

        dataset = self.prepare_dataset(files)
        self.kaggle_api_call(resource='/datasets/create/new', method='POST', body=dataset)

    def prepare_dataset(self, files: list):
        dataset = {}
        if 'dataset_title' in self.config.kaggle:
            dataset['title'] = self.config.kaggle['dataset_title']
        else:
            dataset['title'] = 'Unknown title'
        if 'slug' in self.config.kaggle:
            dataset['slug'] = self.config.kaggle['slug']
        else:
            dataset['slug'] = 'unknown_slug'
        if 'username' in self.config.kaggle:
            dataset['ownerSlug'] = self.config.kaggle['username']
        if 'license' in self.config.kaggle:
            dataset['licenseName'] = self.config.kaggle['license']
        else:
            dataset['licenseName'] = 'CC0-1.0'
        if 'isPrivate' in self.config.kaggle:
            dataset['isPrivate'] = self.config.kaggle['isPrivate']
        else:
            dataset['isPrivate'] = True
        if 'convertToCsv' in self.config.kaggle:
            dataset['convertToCsv'] = self.config.kaggle['convertToCsv']
        else:
            dataset['convertToCsv'] = True
        dataset['files'] = files
        return dataset

    def kaggle_api_call(self, resource, method: str, body=None, post_params=None):
        method = method.upper()
        assert method in ['GET', 'HEAD', 'DELETE', 'POST', 'PUT',
                          'PATCH', 'OPTIONS']
        request_body = json.dumps(body)
        base_uri = "https://www.kaggle.com/api/v1"
        auth_key = urllib3.util.make_headers(
            basic_auth=self.config.kaggle['username'] + ':' + self.config.kaggle['key']
        ).get('authorization')
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json',
                   'User-Agent': 'Swagger-Codegen/1/python', "Authorization": auth_key}
        if post_params is not None:
            del headers['Content-Type']
            return self.pool_manager.request(method=method, url=base_uri + resource, encode_multipart=True,
                                             headers=headers, fields=post_params)
        else:
            return self.pool_manager.request(method=method, url=base_uri + resource, headers=headers, body=request_body)

    def upload_file_to_kaggle(self, file_path: str):
        file_token = None
        try:
            file_name = os.path.basename(file_path)
            content_length = os.path.getsize(file_path)
            last_modified_date_utc = int(os.path.getmtime(file_path))
            post_params = [('fileName', file_name)]
            kaggle_response = self.kaggle_api_call(
                resource='/datasets/upload/file/' + str(content_length) + '/' + str(last_modified_date_utc),
                method='POST',
                post_params=post_params)
            kaggle_data = json.loads(kaggle_response.data.decode('utf8'))
            create_url = kaggle_data['createUrl']
            with io.open(file_path, 'rb', buffering=0) as fp:
                reader = io.BufferedReader(fp)
                session = requests.Session()
                retries = Retry(total=10, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retries)
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                response = session.put(create_url, data=reader)
                if response.status_code == 200 or response.status_code == 201:
                    file_token = kaggle_data['token']
            if file_token is None:
                t.log_message('Upload unsuccessful: ' + file_path)
        except Exception as error:
            t.log_message('Upload filed: ' + file_path + '\n' + str(error))
        return file_token


class WorkspaceConfig:
    def __init__(self, config_yml):
        self.dataset_list: list = None
        self.extract_archives = True
        self.repos: dict = None
        self.script_files: list = None
        self.output_folder: list = None
        self.gdrive_folders: list = None
        self.telegram_channels: list = None
        self.kaggle = None
        if 'dataset_list' in config_yml:
            self.dataset_list = config_yml['dataset_list']
        if 'extract_archives' in config_yml:
            self.extract_archives = config_yml['extract_archives']
        if 'repos' in config_yml:
            self.repos = config_yml['repos']
        if 'script_file' in config_yml:
            self.script_files = config_yml['script_file']
        if 'output_folder' in config_yml:
            self.output_folder = config_yml['output_folder']
        if 'google_drive' in config_yml:
            self.gdrive_folders = config_yml['google_drive']
        if 'telegram_channels' in config_yml:
            self.telegram_channels = config_yml['telegram_channels']
        if 'kaggle' in config_yml:
            self.kaggle = config_yml['kaggle']
