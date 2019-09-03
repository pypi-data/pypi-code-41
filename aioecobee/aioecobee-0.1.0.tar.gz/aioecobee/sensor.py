class EcobeeSensor:
    def __init__(self, sensor):
        self._sensor = sensor

    @property
    def id(self):
        return self._sensor["id"]

    @property
    def name(self):
        return self._sensor["name"]

    @property
    def type(self):
        return self._sensor["type"]

    @property
    def code(self):
        return self._sensor.get("code")

    @property
    def in_use(self):
        return self._sensor["inUse"]

    @property
    def capability(self):
        return self._sensor["capability"]
