from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from jsonconfigfile import Env

def digitalOceanHosting():
    Driver = get_driver(Provider.DIGITAL_OCEAN)
    digitalOcean = Driver(Env().get("DigitalOcean", "Access Token"), api_version='v2')
    return digitalOcean
