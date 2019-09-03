# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pytest_kind']

package_data = \
{'': ['*']}

install_requires = \
['pykube-ng>=0.30.0']

entry_points = \
{'pytest11': ['pytest-kind = pytest_kind.plugin']}

setup_kwargs = {
    'name': 'pytest-kind',
    'version': '19.9.1',
    'description': 'Kubernetes test support with KIND for pytest',
    'long_description': '# pytest-kind\n\n[![Build Status](https://travis-ci.com/hjacobs/pytest-kind.svg?branch=master)](https://travis-ci.com/hjacobs/pytest-kind)\n[![PyPI](https://img.shields.io/pypi/v/pytest-kind)](https://pypi.org/project/pytest-kind/)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pytest-kind)\n![License](https://img.shields.io/github/license/hjacobs/pytest-kind)\n![CalVer](https://img.shields.io/badge/calver-YY.MM.MICRO-22bfda.svg)\n\nTest your Python Kubernetes app/operator end-to-end with [kind](https://kind.sigs.k8s.io/) and [pytest](https://pytest.org).\n\n`pytest-kind` is a plugin for pytest which provides the `kind_cluster` fixture.\nThe fixture will install kind 0.5.1, create a Kubernetes 1.15 cluster, and provide convenience functionality such as port forwarding.\n\n\n## Usage\n\nInstall `pytest-kind` via pip or via [poetry](https://poetry.eustace.io/), e.g.:\n\n```\npoetry add --dev pytest-kind\n```\n\nWrite your pytest functions and use the provided `kind_cluster` fixture, e.g.:\n\n```python\ndef test_kubernetes_version(kind_cluster):\n    assert kind_cluster.api.version == (\'1\', \'15\')\n```\n\nTo load your custom Docker image and apply deployment manifests:\n\n```python\nimport requests\nfrom pykube import Pod\n\ndef test_myapp(kind_cluster):\n    kind_cluster.load_docker_image("myapp")\n    kind_cluster.kubectl("apply", "-f", "deployment.yaml")\n    kind_cluster.kubectl("rollout", "status", "deployment/myapp")\n\n    # using Pykube to query pods\n    for pod in Pod.objects(kind_cluster.api).filter(selector="app=myapp"):\n        assert "Sucessfully started" in pod.logs()\n\n    with kind_cluster.port_forward("service/myapp", 80) as port:\n        r = requests.get(f"http://localhost:{port}/hello/world")\n        r.raise_for_status()\n        assert r.text == "Hello world!"\n```\n\nSee the `examples` directory for sample projects and also check out [kube-web-view](https://codeberg.org/hjacobs/kube-web-view) which uses pytest-kind for its e2e tests.\n\n\n## KindCluster object\n\nThe `kind_cluster` fixture is an instance of the KindCluster class with the following methods:\n\n* `load_docker_image(docker_image)`: load the specified Docker image into the kind cluster\n* `kubectl(*args)`: run the `kubectl` binary against the cluster with the specified arguments. Returns the process output as string.\n* `port_forward(service_or_pod_name, remote_port, *args)`: run "kubectl port-forward" for the given service/pod and return the (random) local port. To be used as context manager ("with" statement). Pass the namespace as additional args to kubectl via "-n", "mynamespace".\n\nKindCluster has the following attributes:\n\n* `name`: the kind cluster name\n* `kubeconfig_path`: the path to the Kubeconfig file to access the cluster\n* `kind_path`: path to the `kind` binary\n* `kubectl_path`: path to the `kubectl` binary\n* `api`: [pykube](https://pykube.readthedocs.io/) HTTPClient instance to access the cluster from Python\n\nYou can also use KindCluster directly without pytest:\n\n```python\nfrom pytest_kind import KindCluster\n\ncluster = KindCluster("myclustername")\ncluster.create()\ncluster.kubectl("apply", "-f", "..")\n# ...\ncluster.delete()\n```\n\n\n## Pytest Options\n\nThe kind cluster name can be set via the `--cluster-name` CLI option.\n\nThe kind cluster is deleted after each pytest session, you can keep the cluster by passing `--keep-cluster` to pytest.\n\n\n## Notes\n\n* The `kind_cluster` fixture is session-scoped, i.e. the same cluster will be used across all test modules/functions.\n* The `kind` and `kubectl` binaries will be downloaded once to the local directory `./.pytest-kind/{cluster-name}/`. You can use them to interact with the cluster (e.g. when `--keep-cluster` is used).\n* Some cluster pods might not be ready immediately (e.g. kind\'s CoreDNS take a moment), add wait/poll functionality as required to make your tests predictable.\n',
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
