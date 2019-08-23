# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['py_jaeger_tracing',
 'py_jaeger_tracing.extractors',
 'py_jaeger_tracing.injectors',
 'py_jaeger_tracing.logger',
 'py_jaeger_tracing.mixin',
 'py_jaeger_tracing.patches',
 'py_jaeger_tracing.utils']

package_data = \
{'': ['*']}

install_requires = \
['jaeger-client>=4.0.0,<5.0.0', 'requests>=2.20.0,<3.0.0']

setup_kwargs = {
    'name': 'py-jaeger-tracing',
    'version': '1.1.8',
    'description': 'Ultimate Python Package for Distribution Tracing',
    'long_description': '# PyJaegerTracing\n\nPyJaegerTracing: Ultimate tool for distribution tracing in Python\n\n\n## Installation\n\n```bash\npip install py-jaeger-tracing\n```\n\n\n## Features\n\n* Multiprocessing support\n* Context / Decorator based tracing\n* Injecting / Extracting tracer span\n* Logger integration\n* Requests integration using patching\n* Boto3 integration using patching\n* Tornado integration\n\n\n# All in One\n\n```\ndocker run -d --name jaeger \\\n  -e COLLECTOR_ZIPKIN_HTTP_PORT=9411 \\\n  -p 5775:5775/udp \\\n  -p 6831:6831/udp \\\n  -p 6832:6832/udp \\\n  -p 5778:5778 \\\n  -p 16686:16686 \\\n  -p 14268:14268 \\\n  -p 9411:9411 \\\n  jaegertracing/all-in-one:1.13\n```',
    'author': 'Mark Andreev',
    'author_email': 'mark.andreev@gmail.com',
    'url': 'https://github.com/mrk-andreev/py_jaeger_tracing',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
