# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['jetblack_messagebus',
 'jetblack_messagebus.authentication',
 'jetblack_messagebus.io']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'jetblack-messagebus-python3',
    'version': '2.2.1',
    'description': 'A python3 client for jetblack-messagebus',
    'long_description': '# jetblack-messagebus-python3\n\nA Python3 client for the [jetblack-messagebus](https://github.com/rob-blackbourn/jetblack-messagebus).\n\n## Example\n\nThe client below subscribes on feed "TEST" to topic "FOO" and prints out \nthe data it receives.\n\n```python\nimport asyncio\n\nfrom jetblack_messagebus import CallbackClient\n\nasync def on_data(user, host, feed, topic, data_packets, is_image):\n    print(f\'data: user="{user}",host="{host}",feed="{feed}",topic="{topic}",is_image={is_image}\')\n    if not data_packets:\n        print("no data")\n    else:\n        for packet in data_packets:\n            message = packet.data.decode(\'utf8\') if packet.data else None\n            print(f\'packet: entitlements={packet.entitlements},message={message}\')\n\nasync def main():\n    """Start the demo"""\n    client = await CallbackClient.create(\'localhost\', 9091)\n    client.data_handlers.append(on_data)\n    await client.add_subscription(\'TEST\', \'FOO\')\n    await client.start()\n\nif __name__ == \'__main__\':\n    asyncio.run(main())\n```',
    'author': 'Rob Blackbourn',
    'author_email': 'rob.blackbourn@googlemail.com',
    'url': 'https://github.com/rob-blackbourn/jetblack-messagebus-python3',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
