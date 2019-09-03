import os
import dataclasses
import threading
import requests

from typing import Optional
from typing import ClassVar
from typing import Union

from gumo.core import GoogleCloudProjectID

from google.cloud import datastore
import google.auth.credentials


class EmulatorCreds(google.auth.credentials.Credentials):
    def __init__(self):
        self.token = b'secret'
        self.expiry = None

    @property
    def valid(self):
        return True

    def refresh(self, _):
        raise RuntimeError('Should never be refreshed.')


@dataclasses.dataclass(frozen=False)
class DatastoreConfiguration:
    google_cloud_project: Union[GoogleCloudProjectID, str, None] = None
    use_local_emulator: bool = False
    emulator_host: Optional[str] = None
    namespace: Optional[str] = None
    client: Optional[datastore.Client] = None

    _ENV_KEY_GOOGLE_CLOUD_PROJECT: ClassVar = 'GOOGLE_CLOUD_PROJECT'
    _ENV_KEY_DATASTORE_EMULATOR_HOST: ClassVar = 'DATASTORE_EMULATOR_HOST'

    _lock: ClassVar = threading.Lock()

    def __post_init__(self):
        with self._lock:
            self._set_google_cloud_project()
            self._set_emulator_config()
            self._set_client()

    def _set_google_cloud_project(self):
        if isinstance(self.google_cloud_project, str):
            self.google_cloud_project = GoogleCloudProjectID(self.google_cloud_project)
        if isinstance(self.google_cloud_project, GoogleCloudProjectID):
            if self.google_cloud_project.value != os.environ.get(self._ENV_KEY_GOOGLE_CLOUD_PROJECT):
                raise RuntimeError(f'Env-var "{self._ENV_KEY_GOOGLE_CLOUD_PROJECT}" is invalid or undefined.'
                                   f'Please set value "{self.google_cloud_project.value}" to env-vars.')

        if self.google_cloud_project is None:
            if self._ENV_KEY_GOOGLE_CLOUD_PROJECT in os.environ:
                self.google_cloud_project = GoogleCloudProjectID(os.environ[self._ENV_KEY_GOOGLE_CLOUD_PROJECT])
            else:
                raise RuntimeError(f'Env-var "{self._ENV_KEY_GOOGLE_CLOUD_PROJECT}" is undefined, please set it.')

    def _set_emulator_config(self):
        emulator_not_configured = not self.use_local_emulator and self.emulator_host is None
        if emulator_not_configured and os.environ.get(self._ENV_KEY_DATASTORE_EMULATOR_HOST):
            self.use_local_emulator = True
            self.emulator_host = os.environ[self._ENV_KEY_DATASTORE_EMULATOR_HOST]

        if not self.use_local_emulator:
            return

        if os.environ.get(self._ENV_KEY_DATASTORE_EMULATOR_HOST) is None:
            raise RuntimeError(
                f'If the emulator enabled, then env-var "{self._ENV_KEY_DATASTORE_EMULATOR_HOST}" must be present.'
            )

        if os.environ.get(self._ENV_KEY_DATASTORE_EMULATOR_HOST) != self.emulator_host:
            host = os.environ.get(self._ENV_KEY_DATASTORE_EMULATOR_HOST)
            raise RuntimeError(
                f'Env-var "{self._ENV_KEY_DATASTORE_EMULATOR_HOST}" and self.emulator_host do not match. '
                f'env["{self._ENV_KEY_DATASTORE_EMULATOR_HOST}"]={host}, self.emulator_host={self.emulator_host}'
            )

    def _set_client(self):
        if isinstance(self.client, datastore.Client):
            return

        if self._ENV_KEY_DATASTORE_EMULATOR_HOST in os.environ:
            emulator_credentials = EmulatorCreds()
            self.client = datastore.Client(
                project=self.google_cloud_project.value,
                namespace=self.namespace,
                credentials=emulator_credentials,
                _http=requests.Session()
            )
            return

        self.client = datastore.Client(
            project=self.google_cloud_project.value,
            namespace=self.namespace,
        )
