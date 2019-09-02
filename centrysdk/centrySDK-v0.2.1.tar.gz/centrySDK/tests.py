import json
from requests import Request

from centrySDK import Centry

auth_code = 'b8cef47fc07a23fd66d7e8f923d2a768c4881c868a22d4537c1d5312ca718610'


c = Centry("94222a6fd57bce789cd6b9e0f8c51095687ab1ca6ca836367c5f65ce7c8dba0e",
           "42e529d544cdc01d32a4fe76270bcdcd135c6146e4c867a4038f9b26ec0e2e6d",
           "urn:ietf:wg:oauth:2.0:oob")
c.refresh_token = 'e649cd56caa6ebbf6664c408af3c8be9bf7cc68a3e830e9740f3d9f560b16971'
auth_url = c.authorization_url('public read_orders write_orders read_products write_products read_integration_config write_integration_config read_user write_user read_webhook write_webhook')
body = c.request('conexion/v1/sizes.json', 'get', {'limit': 5})



