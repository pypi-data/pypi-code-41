# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ocpp', 'ocpp.v16']

package_data = \
{'': ['*'], 'ocpp.v16': ['schemas/*']}

install_requires = \
['jsonschema>=3.0,<4.0']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.6,<0.7']}

setup_kwargs = {
    'name': 'ocpp',
    'version': '0.2.2',
    'description': 'Python package implementing the JSON version of the Open Charge Point Protocol (OCPP).',
    'long_description': '.. image:: https://circleci.com/gh/mobilityhouse/ocpp/tree/master.svg?style=svg\n   :target: https://circleci.com/gh/mobilityhouse/ocpp/tree/master\n\n.. image:: https://img.shields.io/pypi/pyversions/ocpp.svg\n   :target: https://pypi.org/project/ocpp/\n\n.. image:: https://img.shields.io/readthedocs/ocpp.svg\n   :target: https://ocpp.readthedocs.io/en/latest/\n\nOCPP\n----\n\nPython package implementing the JSON version of the Open Charge Point Protocol (OCPP). Currently\nonly OCPP 1.6 is supported.\n\nYou can find the documentation on `rtd`_.\n\nInstallation\n------------\n\nYou can either the project install from Pypi:\n\n.. code-block:: bash\n\n   $ pip install ocpp\n\nOr clone the project and install it manually using:\n\n.. code-block:: bash\n\n   $ pip install .\n\nQuick start\n-----------\n\nBelow you can find examples on how to create a simple charge point as well as a charge point.\n\n.. note::\n\n   To run these examples the dependency websockets_ is required! Install it by running:\n\n   .. code-block:: bash\n\n      $ pip install websockets\n\nCentral system\n~~~~~~~~~~~~~~\n\nThe code snippet below creates a simple central system which is able to handle BootNotification\ncalls. You can find a detailed explaination of the code in the `Central System documentation_`.\n\n\n.. code-block:: python\n\n   import asyncio\n   import websockets\n   from datetime import datetime\n\n   from ocpp.routing import on\n   from ocpp.v16 import ChargePoint as cp\n   from ocpp.v16.enums import Action, RegistrationStatus\n   from ocpp.v16 import call_result\n\n\n   class ChargePoint(cp):\n       @on(Action.BootNotification)\n       def on_boot_notitication(self, charge_point_vendor, charge_point_model, **kwargs):\n           return call_result.BootNotificationPayload(\n               current_time=datetime.utcnow().isoformat(),\n               interval=10,\n               status=RegistrationStatus.accepted\n           )\n\n\n   async def on_connect(websocket, path):\n       """ For every new charge point that connects, create a ChargePoint instance\n       and start listening for messages.\n\n       """\n       charge_point_id = path.strip(\'/\')\n       cp = ChargePoint(charge_point_id, websocket)\n\n       await cp.start()\n\n\n   async def main():\n       server = await websockets.serve(\n           on_connect,\n           \'0.0.0.0\',\n           9000,\n           subprotocols=[\'ocpp1.6\']\n       )\n\n       await server.wait_closed()\n\n\n   if __name__ == \'__main__\':\n       asyncio.run(main())\n\nCharge point\n~~~~~~~~~~~~\n\n.. code-block:: python\n\n   import asyncio\n   import websockets\n\n   from ocpp.v16 import call, ChargePoint as cp\n   from ocpp.v16.enums import RegistrationStatus\n\n\n   class ChargePoint(cp):\n       async def send_boot_notification(self):\n           request = call.BootNotificationPayload(\n               charge_point_model="Optimus",\n               charge_point_vendor="The Mobility House"\n           )\n\n           response = await self.call(request)\n\n           if response.status ==  RegistrationStatus.accepted:\n               print("Connected to central system.")\n\n\n   async def main():\n       async with websockets.connect(\n           \'ws://localhost:9000/CP_1\',\n            subprotocols=[\'ocpp1.6\']\n       ) as ws:\n\n           cp = ChargePoint(\'CP_1\', ws)\n\n           await asyncio.gather(cp.start(), cp.send_boot_notification())\n\n\n   if __name__ == \'__main__\':\n       asyncio.run(main())\n\nLicense\n-------\n\nExcept from the documents in `docs/v16/specification/` everything is licensed under MIT_.\n© `The Mobility House`_\n\nThe documents in `docs/v16/specification/` are licensed under Creative Commons\nAttribution-NoDerivatives 4.0 International Public License.\n\n.. _Central System documentation: https://ocpp.readthedocs.io/en/latest/central_system.html\n.. _MIT: https://github.com/mobilityhouse/ocpp/blob/master/LICENSE\n.. _rtd: https://ocpp.readthedocs.io/en/latest/index.html\n.. _The Mobility House: https://www.mobilityhouse.com/int_en/\n.. _websockets: https://pypi.org/project/websockets/\n',
    'author': 'Andre Duarte',
    'author_email': 'andre.duarte@mobilityhouse.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
