# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pytest_kind']

package_data = \
{'': ['*']}

install_requires = \
['pykube-ng>=0.30.0,<0.31.0']

entry_points = \
{'pytest11': ['pytest-kind = pytest_kind.plugin']}

setup_kwargs = {
    'name': 'pytest-kind',
    'version': '0.4.0',
    'description': 'Kubernetes test support with KIND for pytest',
    'long_description': '# pytest-kind\n\nTest your Python Kubernetes app/operator end-to-end with [kind](https://kind.sigs.k8s.io/) and [pytest](https://pytest.org).\n\n`pytest-kind` is a plugin for pytest which provides the `kind_cluster` fixture.\nThe fixture will install kind, create a cluster, and provide convenience functionality such as port forwarding.\n\n## Usage\n\nInstall `pytest-kind` via pip or via poetry, e.g.:\n\n```\npoetry add --dev pytest-kind\n```\n\nWrite your pytest functions and use the provided `kind_cluster` fixture, e.g.:\n\n```\ndef test_kubernetes_version(kind_cluster):\n    assert kind_cluster.api.version == (\'1\', \'15\')\n```\n\nTo load your custom Docker image and apply deployment manifests:\n\n```\nfrom pykube import Pod\n\ndef test_myapp(kind_cluster):\n    kind_cluster.load_docker_image("myapp")\n    kind_cluster.kubectl("apply", "-f", "deployment.yaml")\n    kind_cluster.kubectl("rollout", "status", "deployment/myapp")\n\n    # using Pykube to query pods\n    for pod in Pod.objects(kind_cluster.api).filter(selector="app=myapp"):\n        assert "Sucessfully started" in pod.logs()\n```\n\nSee the `examples` directory for sample projects.\n\n## Pytest Options\n\nThe kind cluster name can be set via the `--cluster-name` CLI option.\n\nThe kind cluster is deleted after each pytest session, you can keep the cluster by passing `--keep-cluster` to pytest.\n',
    'author': 'Henning Jacobs',
    'author_email': 'henning@jacobs1.de',
    'url': 'https://codeberg.org/hjacobs/pytest-kind',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
