import aiofiles
import json
import logging
import os

from .const import (
    API_URL,
    API_VERSION,
    ECOBEE_API_KEY,
    ECOBEE_REFRESH_TOKEN,
    ENDPOINT_PIN,
    ENDPOINT_THERMOSTAT,
    ENDPOINT_TOKEN,
)
from .errors import AuthCodeEmptyError, ExpiredTokensError, RefreshTokenEmptyError
from .sensor import EcobeeSensor
from .thermostat import EcobeeThermostat

_LOGGER = logging.getLogger(__name__)


class EcobeeAPI:
    """Main class to interact with the Ecobee API asynchronously."""

    def __init__(self, session, api_key=None, config_file=None, refresh_token=None):
        """Initialize the API object."""
        self._session = session
        self._config_file = config_file
        self._pin = None
        self._authorization_code = None
        self._access_token = None
        self._ecobee_config = {
            ECOBEE_API_KEY: api_key,
            ECOBEE_REFRESH_TOKEN: refresh_token,
        }
        self.sensors = {}
        self.thermostats = {}

    @property
    def config(self):
        return self._ecobee_config

    @property
    def pin(self):
        return self._pin

    @property
    def is_authorized(self):
        return self._ecobee_config[ECOBEE_REFRESH_TOKEN] is not None

    async def get_all_devices(self):
        """Populate all devices in the Ecobee account."""
        param_string = {
            "selection": {
                "selectionType": "registered",
                "includeRuntime": "true",
                "includeSensors": "true",
                "includeProgram": "true",
                "includeEquipmentStatus": "true",
                "includeEvents": "true",
                "includeWeather": "true",
                "includeSettings": "true",
            }
        }

        params = {"json": json.dumps(param_string)}

        result = await self._request(
            "get", ENDPOINT_THERMOSTAT, params=params, auth=True
        )
        try:
            for item in result["thermostatList"]:
                thermostat = EcobeeThermostat(item, self._request)
                self.thermostats[thermostat.identifier] = thermostat
                for sensor_item in thermostat.remoteSensors:
                    sensor = EcobeeSensor(sensor_item)
                    self.sensors[sensor.id] = sensor

        except (KeyError, TypeError) as err:
            _LOGGER.error("Error requesting thermostats from Ecobee: {}".format(err))

    async def update(self):
        """Wrapper for get_all_devices."""
        await self.get_all_devices()

    async def request_pin(self):
        """Request PIN and authorization code from Ecobee."""
        params = {
            "response_type": "ecobeePin",
            "client_id": self._ecobee_config[ECOBEE_API_KEY],
            "scope": "smartWrite",
        }

        result = await self._request("get", path=ENDPOINT_PIN, params=params)
        try:
            self._authorization_code = result["code"]
            self._pin = result["ecobeePin"]
            _LOGGER.debug(
                "Obtained pin ({}) and authorization code ({})".format(
                    self._pin, self._authorization_code
                )
            )
        except (KeyError, TypeError) as err:
            _LOGGER.error("Error requesting PIN from Ecobee.: {}".format(err))

    async def request_tokens(self):
        """Request access and refresh tokens from Ecobee."""
        if self._authorization_code is None:
            raise AuthCodeEmptyError(
                "No authorization code available; request PIN first."
            )

        params = {
            "grant_type": "ecobeePin",
            "code": self._authorization_code,
            "client_id": self._ecobee_config[ECOBEE_API_KEY],
        }

        result = await self._request("post", path=ENDPOINT_TOKEN, params=params)
        try:
            self._access_token = result["access_token"]
            self._ecobee_config[ECOBEE_REFRESH_TOKEN] = result["refresh_token"]
            if self._config_file is not None:
                await self._write_config_to_file()
            _LOGGER.debug(
                "Obtained access token ({}) and refresh token ({})".format(
                    self._access_token, self._ecobee_config[ECOBEE_REFRESH_TOKEN]
                )
            )
        except (KeyError, TypeError) as err:
            _LOGGER.error("Error requesting tokens from Ecobee: {}".format(err))

    async def refresh_tokens(self):
        """Refresh access and refresh tokens from Ecobee."""
        if self._ecobee_config[ECOBEE_REFRESH_TOKEN] is None:
            raise RefreshTokenEmptyError(
                "No refresh token available; request tokens first."
            )

        params = {
            "grant_type": "refresh_token",
            "refresh_token": self._ecobee_config[ECOBEE_REFRESH_TOKEN],
            "client_id": self._ecobee_config[ECOBEE_API_KEY],
        }

        result = await self._request("post", path=ENDPOINT_TOKEN, params=params)
        try:
            self._access_token = result["access_token"]
            self._ecobee_config[ECOBEE_REFRESH_TOKEN] = result["refresh_token"]
            if self._config_file is not None:
                await self._write_config_to_file()
            _LOGGER.debug(
                "Refreshed access token ({}) and refresh token ({})".format(
                    self._access_token, self._ecobee_config[ECOBEE_REFRESH_TOKEN]
                )
            )
        except (KeyError, TypeError) as err:
            _LOGGER.error("Error refreshing tokens from Ecobee: {}".format(err))

    async def load_config_from_file(self):
        if self._config_file is not None:
            """Attempt to load existing config from passed-in config file."""
            if os.path.isfile(self._config_file):
                """File exists, read config from it."""
                try:
                    async with aiofiles.open(self._config_file, "r") as f:
                        config = json.loads(await f.read())
                    if config is not None:
                        self._ecobee_config[ECOBEE_API_KEY] = config.get(ECOBEE_API_KEY)
                        self._ecobee_config[ECOBEE_REFRESH_TOKEN] = config.get(
                            ECOBEE_REFRESH_TOKEN
                        )
                except IOError:
                    _LOGGER.error("Error reading file: {}".format(self._config_file))

    async def _write_config_to_file(self):
        """Write updated config to passed-in config file."""
        try:
            async with aiofiles.open(self._config_file, "w") as f:
                await f.write(json.dumps(self._ecobee_config))
            _LOGGER.debug("Wrote Ecobee config to {}".format(self._config_file))
        except IOError:
            _LOGGER.error("Error writing file: {}".format(self._config_file))

    async def _request(
        self, method, path=ENDPOINT_THERMOSTAT, params=None, json=None, auth=False
    ):
        """Make an async request to the Ecobee API."""
        from aiohttp import ClientResponseError

        headers = {}

        if auth:
            url = "{}/{}/{}".format(API_URL, API_VERSION, path)
            headers["Content-Type"] = "application/json;charset=UTF-8"
            headers["Authorization"] = "Bearer {}".format(self._access_token)
        else:
            url = "{}/{}".format(API_URL, path)

        try:
            async with self._session.request(
                method, url, params=params, headers=headers, json=json
            ) as result:
                result.raise_for_status()
                return await result.json()
        except ClientResponseError as err:
            _LOGGER.error("Ecobee API request error: {}".format(err))
            if result.status == 400:
                raise ExpiredTokensError(
                    "Tokens expired. Request new tokens from ecobee."
                )
