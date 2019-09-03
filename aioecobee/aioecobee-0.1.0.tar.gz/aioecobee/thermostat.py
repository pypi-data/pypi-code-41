from .const import DEFAULT_MESSAGE, ECOBEE_HVAC_MODE_AUTO, HOLD_TYPE_NEXTRANSITION


class EcobeeThermostat:
    def __init__(self, thermostat, request):
        self._thermostat = thermostat
        self._request = request

    @property
    def identifier(self):
        return self._thermostat["identifier"]

    @property
    def name(self):
        return self._thermostat["name"]

    @property
    def thermostatRev(self):
        return self._thermostat["thermostatRev"]

    @property
    def isRegistered(self):
        return self._thermostat["isRegistered"]

    @property
    def modelNumber(self):
        return self._thermostat["modelNumber"]

    @property
    def brand(self):
        return self._thermostat["brand"]

    @property
    def features(self):
        return self._thermostat["features"]

    @property
    def lastModified(self):
        return self._thermostat["lastModified"]

    @property
    def thermostatTime(self):
        return self._thermostat["thermostatTime"]

    @property
    def utcTime(self):
        return self._thermostat["utcTime"]

    @property
    def settings(self):
        return self._thermostat["settings"]

    @property
    def runtime(self):
        return self._thermostat["runTime"]

    @property
    def weather(self):
        return self._thermostat["weather"]

    @property
    def events(self):
        return self._thermostat["events"]

    @property
    def program(self):
        return self._thermostat["program"]

    @property
    def equipmentStatus(self):
        return self._thermostat["equipmentStatus"]

    @property
    def remoteSensors(self):
        return self._thermostat["remoteSensors"]

    async def set_hvac_mode(self, hvac_mode=ECOBEE_HVAC_MODE_AUTO):
        """Possible modes are: auto, auxHeatOnly, cool, heat, off."""
        json = {
            "selection": {
                "selectionType": "thermostats",
                "selectionMatch": self.identifier,
                "thermostat": {"settings": {"hvacMode": hvac_mode}},
            }
        }

        await self._request("post", json=json, auth=True)

    async def set_fan_min_on_time(self, time: int):
        """Minimum time to run the fan each hour. Int from 1 to 60."""
        json = {
            "selection": {
                "selectionType": "thermostats",
                "selectionMatch": self.identifier,
                "thermostat": {"settings": {"fanMinOnTime": time}},
            }
        }

        await self._request("post", json=json, auth=True)

    async def set_fan_mode(
        self, fan_mode, cool_temp, heat_temp, hold_type=HOLD_TYPE_NEXTRANSITION
    ):
        """Possible modes are: auto, minontime, on."""
        json = {
            "selection": {
                "selectionType": "thermostats",
                "selectionMatch": self.identifier,
                "functions": [
                    {
                        "type": "setHold",
                        "params": {
                            "holdType": hold_type,
                            "coolHoldTemp": int(cool_temp * 10),
                            "heatHoldTemp": int(heat_temp * 10),
                            "fan": fan_mode,
                        },
                    }
                ],
            }
        }

        await self._request("post", json=json, auth=True)

    async def set_hold_temp(
        self, cool_temp, heat_temp, hold_type=HOLD_TYPE_NEXTRANSITION
    ):
        """Set a hold temperature."""
        json = {
            "selection": {
                "selectionType": "thermostats",
                "selectionMatch": self.identifier,
                "functions": [
                    {
                        "type": "setHold",
                        "params": {
                            "holdType": hold_type,
                            "coolHoldTemp": int(cool_temp * 10),
                            "heatHoldTemp": int(heat_temp * 10),
                        },
                    }
                ],
            }
        }

        await self._request("post", json=json, auth=True)

    async def set_climate_hold(self, climate, hold_type=HOLD_TYPE_NEXTRANSITION):
        """Set a climate hold (e.g. away, home, sleep)."""
        json = {
            "selection": {
                "selectionType": "thermostats",
                "selectionMatch": self.identifier,
            },
            "functions": [
                {
                    "type": "setHold",
                    "params": {"holdType": hold_type, "holdClimateRef": climate},
                }
            ],
        }

        await self._request("post", json=json, auth=True)

    async def delete_vacation(self, vacation):
        """Delete a vacation."""
        json = {
            "selection": {
                "selectionType": "thermostats",
                "selectionMatch": self.identifier,
            },
            "functions": [{"type": "deleteVacation", "params": {"name": vacation}}],
        }

        await self._request("post", json=json, auth=True)

    async def resume_program(self, resume_all=False):
        """Resume currently scheduled program."""
        json = {
            "selection": {
                "selectionType": "thermostats",
                "selectionMatch": self.identifier,
            },
            "functions": [
                {"type": "resumeProgram", "params": {"resumeAll": resume_all}}
            ],
        }

        await self._request("post", json=json, auth=True)

    async def send_message(self, message=DEFAULT_MESSAGE):
        """Send the first 500 chars of the message to the thermostat."""
        json = {
            "selection": {
                "selectionType": "thermostats",
                "selectionMatch": self.identifier,
            },
            "functions": [{"type": "sendMessage", "params": {"text": message[0:500]}}],
        }

        await self._request("post", json=json, auth=True)

    async def set_humidity(self, humidity: int):
        """Set the humidity level."""
        json = {
            "selection": {
                "selectionType": "thermostats",
                "selectionMatch": self.identifier,
            },
            "thermostat": {"settings": {"humidity": humidity}},
        }

        await self._request("post", json=json, auth=True)

    async def set_mic_mode(self, mic_enabled=True):
        """Enable/Disable the Alexa microphone (ecobee4 only)."""
        json = {
            "selection": {
                "selectionType": "thermostats",
                "selectionMatch": self.identifier,
            },
            "thermostat": {"audio": {"microphoneEnabled": mic_enabled}},
        }

        await self._request("post", json=json, auth=True)

    async def set_occupancy_modes(self, auto_away=False, follow_me=False):
        """Enable/Disable Smart Home/Away and Follow Me modes."""
        json = {
            "selection": {
                "selectionType": "thermostats",
                "selectionMatch": self.identifier,
            },
            "thermostat": {
                "settings": {"autoAway": auto_away, "followMeComfort": follow_me}
            },
        }

        await self._request("post", json=json, auth=True)

    async def set_dst_mode(self, dst=True):
        """Enable/Disable Daylight Savings."""
        json = {
            "selection": {
                "selectionType": "thermostats",
                "selectionMatch": self.identifier,
            },
            "thermostat": {"location": {"isDaylightSaving": dst}},
        }

        await self._request("post", json=json, auth=True)
