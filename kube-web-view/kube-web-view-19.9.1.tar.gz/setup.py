# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['kube_web']

package_data = \
{'': ['*'],
 'kube_web': ['templates/*', 'templates/assets/*', 'templates/partials/*']}

install_requires = \
['Jinja2>=2.10,<3.0',
 'Pygments>=2.4,<3.0',
 'aioauth-client>=0.17.3,<0.18.0',
 'aiohttp-jinja2>=1.1,<2.0',
 'aiohttp_remotes>=0.1.2,<0.2.0',
 'aiohttp_session[secure]>=2.7,<3.0',
 'jmespath>=0.9.4,<0.10.0',
 'pykube-ng>=19.9.0']

entry_points = \
{'console_scripts': ['kube-web-view = kube_web:main.main']}

setup_kwargs = {
    'name': 'kube-web-view',
    'version': '19.9.1',
    'description': 'Kubernetes Web View allows to list and view all Kubernetes resources (incl. CRDs) with permalink-friendly URLs in a plain-HTML frontend',
    'long_description': '# Kubernetes Web View\n\n[![Build Status](https://travis-ci.com/hjacobs/kube-web-view.svg?branch=master)](https://travis-ci.com/hjacobs/kube-web-view)\n[![Documentation Status](https://readthedocs.org/projects/kube-web-view/badge/?version=latest)](https://kube-web-view.readthedocs.io/en/latest/?badge=latest)\n![GitHub tag (latest SemVer)](https://img.shields.io/github/tag/hjacobs/kube-web-view)\n![Docker Pulls](https://img.shields.io/docker/pulls/hjacobs/kube-web-view.svg)\n![License](https://img.shields.io/github/license/hjacobs/kube-web-view)\n![CalVer](https://img.shields.io/badge/calver-YY.MM.MICRO-22bfda.svg)\n\nKubernetes Web View allows to list and view all Kubernetes resources (incl. CRDs) with permalink-friendly URLs in a plain-HTML frontend.\nThis tool was mainly developed to provide a web-version of `kubectl` for troubleshooting and supporting colleagues.\nSee the [Kubernetes Web View Documentation](https://kube-web-view.readthedocs.io/) and [try out the live demo](https://kube-web-view.demo.j-serv.de/).\n\nGoals:\n\n* handling of any API resource: both core Kubernetes and CRDs\n* permalink-friendly URL paths for giving links to colleagues (e.g. to help troubleshoot)\n* option to work with multiple clusters\n* allow listing different resource types on the same page (e.g. deployments and CRDs with same label)\n* replicate some of the common `kubectl` features, e.g. `-l` (label selector) and `-L` (label columns)\n* simple HTML, only add JavaScript where it adds value\n* pluggable links, e.g. to link to other tools based on resource properties like labels (monitoring, reports, ..)\n* optional: editing resources as YAML manifests (`kubectl edit`)\n\nNon-goals:\n\n* application management\n* reporting/visualization\n* fancy UI (JS/SPA)\n\n## Quickstart\n\nThis will run Kubernetes Web View locally with your existing Kubeconfig:\n\n```\ndocker run -it -p 8080:8080 -u $(id -u) -v $HOME/.kube:/.kube hjacobs/kube-web-view\n```\n\nOpen http://localhost:8080/ in your browser to see the UI.\n\n## Deploying into your cluster\n\nThis will deploy a single Pod with Kubernetes Web View into your cluster:\n\n```\nkubectl apply -f deploy/\nkubectl port-forward service/kube-web-view 8080:80\n```\n\nOpen http://localhost:8080/ in your browser to see the UI.\n\n\n## Running tests\n\nThis requires Python 3.7 and [poetry](https://poetry.eustace.io/) and will run unit tests and end-to-end tests with [Kind](https://github.com/kubernetes-sigs/kind):\n\n```\nmake test\n```\n\nThe end-to-end (e2e) tests will bootstrap a new Kind cluster via [pytest-kind](https://pypi.org/project/pytest-kind/), you can keep the cluster and run Kubernetes Web View for development against it:\n\n```\nPYTEST_OPTIONS=--keep-cluster make test\nmake run.kind\n```\n\n\n## Building the Docker image\n\n```\nmake\n```\n\n\n## Developing Locally\n\nTo start the Python web server locally with the default kubeconfig (`~/.kube/config`):\n\n```\nmake run\n```\n',
    'author': 'Henning Jacobs',
    'author_email': 'henning@zalando.de',
    'url': 'https://kube-web-view.readthedocs.io/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
