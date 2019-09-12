#!/usr/bin/env python3
import os

from setuptools import setup, find_packages
from subprocess import check_call

setup(
    name="indico_install",
    version="0.1",
    description="An indico install platform",
    author="Indico",
    author_email="engineering@indico.io",
    packages=find_packages(),
    install_requires=[
        "click",
        "pyyaml==5.1.2",
        "requests",
        "psycopg2-binary",
        "cached_property",
        "google-cloud-storage==1.17.0",
    ],
    extras_require={"aks": ["azure-cli"], "eks": ["boto3==1.9.176"]},
    scripts=["bin/indico", "bin/kube"]
    + [f"bin/kube_bin/{filename}" for filename in os.listdir("bin/kube_bin")],
)

check_call(
    [
        "bash",
        "-c",
        'azcomm=$(command -v az); if ! [ -z "$azcomm" ]; then sed -i "s/^python /python3 /g" $azcomm; fi',
    ]
)
