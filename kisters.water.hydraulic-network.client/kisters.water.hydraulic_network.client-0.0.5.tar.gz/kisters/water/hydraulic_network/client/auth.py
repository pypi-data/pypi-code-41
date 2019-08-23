from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import requests


class Authentication(ABC):
    @abstractmethod
    def get_access_token(self) -> str:
        """Provide the caller an access token"""


class OpenIDConnect(Authentication):
    """OpenID connect authentication implementation."""

    def __init__(
        self,
        issuer_url: str,
        client_id: str,
        client_secret: str,
        access_token_expiration_buffer: float = 30.0,  # seconds
    ):
        super().__init__()
        self._issuer_url = issuer_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._configuration = None
        self._access_token = None
        self._access_token_expiration = None
        self._access_token_expiration_buffer = access_token_expiration_buffer
        self._refresh_token = None
        self._refresh_token_expiration = None

    def get_access_token(self, refresh: bool = False) -> str:
        if (
            refresh
            or not self._access_token
            or self._access_token_expiration < datetime.utcnow()
        ):
            self._retrieve_access_token()
        return self._access_token

    def get_refresh_token(self, refresh: bool = False) -> str:
        if (
            refresh
            or not self._refresh_token
            or self._refresh_token_expiration < datetime.utcnow()
        ):
            self._retrieve_refresh_token()
        return self._refresh_token

    @property
    def configuration(self) -> dict:
        if not self._configuration:
            response = requests.get(
                url=self._issuer_url + "/.well-known/openid-configuration"
            )
            response.raise_for_status()
            self._configuration = response.json()
        return self._configuration

    def _retrieve_refresh_token(self):
        response = requests.post(
            url=self.configuration["token_endpoint"],
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        token_data = response.json()
        self._refresh_token = token_data["refresh_token"]
        self._refresh_token_expiration = datetime.utcnow() + timedelta(
            seconds=(
                token_data["refresh_expires_in"] - self._access_token_expiration_buffer
            )
        )
        if "access_token" in token_data:
            self._access_token = token_data["access_token"]
            self._access_token_expiration = datetime.utcnow() + timedelta(
                seconds=(
                    token_data["expires_in"] - self._access_token_expiration_buffer
                )
            )

    def _retrieve_access_token(self):
        refresh_token = self.get_refresh_token()
        if not self._access_token or self._access_token_expiration < datetime.utcnow():
            response = requests.post(
                url=self.configuration["token_endpoint"],
                data={
                    "grant_type": "refresh_token",
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "refresh_token": refresh_token,
                },
                headers={"content-type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            token_data = response.json()
            if "refresh_token" in token_data:
                self._refresh_token = token_data["refresh_token"]
                self._refresh_token_expiration = datetime.utcnow() + timedelta(
                    seconds=(
                        token_data["refresh_expires_in"]
                        - self._access_token_expiration_buffer
                    )
                )
            self._access_token = token_data["access_token"]
            self._access_token_expiration = datetime.utcnow() + timedelta(
                seconds=(
                    token_data["expires_in"] - self._access_token_expiration_buffer
                )
            )


class TemporaryAccess(Authentication):
    def __init__(self, access_token: str):
        super().__init__()
        self._access_token = access_token

    def get_access_token(self) -> str:
        return self._access_token
